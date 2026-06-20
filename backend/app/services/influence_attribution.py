"""
Post-simulation Influence Attribution Service.

Analyzes completed simulation action logs to produce:
- Agent influence scores (who shaped the conversation most)
- Influence chains (A → B → C propagation paths)
- Top influencers per platform
- Cross-platform influence bridges
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import math

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('kephalosdata.influence')


@dataclass
class AgentInfluenceNode:
    agent_id: int
    agent_name: str
    platforms: List[str] = field(default_factory=list)
    # Outgoing influence: posts that others interacted with
    posts_created: int = 0
    posts_reposted_by_others: int = 0
    posts_quoted_by_others: int = 0
    posts_liked_by_others: int = 0
    posts_commented_on: int = 0
    # Incoming influence: interactions received
    unique_agents_reached: int = 0
    reach_set: set = field(default_factory=set)
    # Cross-platform influence
    cross_platform_bridges: int = 0
    # Computed score
    influence_score: float = 0.0

    def compute_score(self):
        """Weighted influence score. Reposts and quotes carry more weight than likes."""
        self.unique_agents_reached = len(self.reach_set)
        self.influence_score = (
            self.posts_reposted_by_others * 5.0
            + self.posts_quoted_by_others * 4.0
            + self.posts_commented_on * 3.0
            + self.posts_liked_by_others * 1.0
            + self.unique_agents_reached * 2.0
            + self.cross_platform_bridges * 3.0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "platforms": self.platforms,
            "posts_created": self.posts_created,
            "posts_reposted_by_others": self.posts_reposted_by_others,
            "posts_quoted_by_others": self.posts_quoted_by_others,
            "posts_liked_by_others": self.posts_liked_by_others,
            "posts_commented_on": self.posts_commented_on,
            "unique_agents_reached": self.unique_agents_reached,
            "cross_platform_bridges": self.cross_platform_bridges,
            "influence_score": round(self.influence_score, 2),
        }


@dataclass
class InfluenceEdge:
    from_agent_id: int
    from_agent_name: str
    to_agent_id: int
    to_agent_name: str
    interaction_type: str  # repost, quote, like, comment
    platform: str
    weight: float = 1.0

    def to_dict(self):
        return {
            "from": {"id": self.from_agent_id, "name": self.from_agent_name},
            "to": {"id": self.to_agent_id, "name": self.to_agent_name},
            "type": self.interaction_type,
            "platform": self.platform,
            "weight": self.weight,
        }


class InfluenceAttributionService:
    """Analyzes completed simulation logs to attribute influence."""

    # Weights for different interaction types
    INTERACTION_WEIGHTS = {
        "repost": 5.0,
        "quote": 4.0,
        "comment": 3.0,
        "like": 1.0,
        "dislike": 0.5,
    }

    def __init__(self, simulation_dir: str):
        self.simulation_dir = simulation_dir
        self._nodes: Dict[int, AgentInfluenceNode] = {}
        self._edges: List[InfluenceEdge] = []
        # post_id → {agent_id, agent_name, platform}
        self._post_registry: Dict[str, Dict] = {}
        # Aggregate edges: (from_id, to_id) → total_weight
        self._edge_weights: Dict[Tuple[int, int], float] = defaultdict(float)

    def _get_or_create_node(self, agent_id: int, agent_name: str, platform: str) -> AgentInfluenceNode:
        if agent_id not in self._nodes:
            self._nodes[agent_id] = AgentInfluenceNode(
                agent_id=agent_id, agent_name=agent_name
            )
        node = self._nodes[agent_id]
        if platform not in node.platforms:
            node.platforms.append(platform)
        return node

    def _load_platform_actions(self, platform: str) -> List[Dict]:
        """Load all actions from a platform's actions.jsonl."""
        path = os.path.join(self.simulation_dir, platform, "actions.jsonl")
        if not os.path.exists(path):
            return []
        actions = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if "event_type" not in entry and "action_type" in entry:
                        entry["platform"] = platform
                        actions.append(entry)
                except json.JSONDecodeError:
                    continue
        return actions

    def _process_action(self, action: Dict):
        """Process a single action to update influence graph."""
        agent_id = action.get("agent_id")
        agent_name = action.get("agent_name", f"Agent_{agent_id}")
        action_type = action.get("action_type", "").upper()
        action_args = action.get("action_args", {})
        platform = action.get("platform", "twitter")

        if agent_id is None:
            return

        actor_node = self._get_or_create_node(agent_id, agent_name, platform)

        # Register posts
        if action_type == "CREATE_POST":
            new_post_id = str(action_args.get("new_post_id", ""))
            if new_post_id:
                self._post_registry[new_post_id] = {
                    "agent_id": agent_id, "agent_name": agent_name, "platform": platform
                }
            actor_node.posts_created += 1

        # Repost: actor → original post creator
        elif action_type == "REPOST":
            orig_post_id = str(action_args.get("post_id", ""))
            origin = self._post_registry.get(orig_post_id)
            if origin and origin["agent_id"] != agent_id:
                origin_node = self._get_or_create_node(
                    origin["agent_id"], origin["agent_name"], origin["platform"]
                )
                origin_node.posts_reposted_by_others += 1
                origin_node.reach_set.add(agent_id)
                # Cross-platform bridge
                if origin["platform"] != platform:
                    origin_node.cross_platform_bridges += 1
                self._edge_weights[(origin["agent_id"], agent_id)] += self.INTERACTION_WEIGHTS["repost"]
                self._edges.append(InfluenceEdge(
                    origin["agent_id"], origin["agent_name"],
                    agent_id, agent_name, "repost", platform,
                    self.INTERACTION_WEIGHTS["repost"]
                ))

        # Quote post
        elif action_type == "QUOTE_POST":
            orig_post_id = str(action_args.get("post_id", action_args.get("quoted_id", "")))
            origin = self._post_registry.get(orig_post_id)
            if origin and origin["agent_id"] != agent_id:
                origin_node = self._get_or_create_node(
                    origin["agent_id"], origin["agent_name"], origin["platform"]
                )
                origin_node.posts_quoted_by_others += 1
                origin_node.reach_set.add(agent_id)
                self._edge_weights[(origin["agent_id"], agent_id)] += self.INTERACTION_WEIGHTS["quote"]
                self._edges.append(InfluenceEdge(
                    origin["agent_id"], origin["agent_name"],
                    agent_id, agent_name, "quote", platform,
                    self.INTERACTION_WEIGHTS["quote"]
                ))

        # Like post
        elif action_type == "LIKE_POST":
            liked_post_id = str(action_args.get("post_id", action_args.get("like_id", "")))
            origin = self._post_registry.get(liked_post_id)
            if origin and origin["agent_id"] != agent_id:
                origin_node = self._get_or_create_node(
                    origin["agent_id"], origin["agent_name"], origin["platform"]
                )
                origin_node.posts_liked_by_others += 1
                origin_node.reach_set.add(agent_id)
                self._edge_weights[(origin["agent_id"], agent_id)] += self.INTERACTION_WEIGHTS["like"]

        # Comment
        elif action_type == "CREATE_COMMENT":
            post_id = str(action_args.get("post_id", ""))
            origin = self._post_registry.get(post_id)
            if origin and origin["agent_id"] != agent_id:
                origin_node = self._get_or_create_node(
                    origin["agent_id"], origin["agent_name"], origin["platform"]
                )
                origin_node.posts_commented_on += 1
                origin_node.reach_set.add(agent_id)
                self._edge_weights[(origin["agent_id"], agent_id)] += self.INTERACTION_WEIGHTS["comment"]

    def _run_pagerank(self, iterations: int = 20, damping: float = 0.85):
        """Simple PageRank to refine influence scores."""
        if not self._nodes:
            return
        n = len(self._nodes)
        scores = {nid: 1.0 / n for nid in self._nodes}
        for _ in range(iterations):
            new_scores = {nid: (1 - damping) / n for nid in self._nodes}
            for (from_id, to_id), weight in self._edge_weights.items():
                if from_id in self._nodes:
                    out_weight = sum(
                        w for (fid, _), w in self._edge_weights.items() if fid == from_id
                    ) or 1
                    new_scores[to_id] = new_scores.get(to_id, 0) + damping * scores[from_id] * (weight / out_weight)
            total = sum(new_scores.values()) or 1
            scores = {k: v / total for k, v in new_scores.items()}
        # Blend PageRank with raw influence score
        for node_id, node in self._nodes.items():
            node.compute_score()
            pr = scores.get(node_id, 0)
            node.influence_score = round(node.influence_score * 0.7 + pr * n * 30, 2)

    def analyze(self) -> Dict[str, Any]:
        """
        Run full influence analysis on the simulation.
        Returns structured results.
        """
        platforms = ["twitter", "reddit"]
        all_actions = []
        for platform in platforms:
            all_actions.extend(self._load_platform_actions(platform))

        if not all_actions:
            return {"error": "No action logs found", "simulation_dir": self.simulation_dir}

        # Sort by round then timestamp for deterministic processing
        all_actions.sort(key=lambda x: (x.get("round", 0), x.get("timestamp", "")))

        for action in all_actions:
            self._process_action(action)

        self._run_pagerank()

        # Build top influencers list
        sorted_nodes = sorted(
            self._nodes.values(),
            key=lambda n: n.influence_score,
            reverse=True
        )

        top_influencers = [n.to_dict() for n in sorted_nodes[:20]]

        # Build influence network (top edges by weight)
        top_edges = sorted(
            [
                {
                    "from_id": fid,
                    "from_name": self._nodes[fid].agent_name if fid in self._nodes else f"Agent_{fid}",
                    "to_id": tid,
                    "to_name": self._nodes[tid].agent_name if tid in self._nodes else f"Agent_{tid}",
                    "weight": round(w, 2),
                }
                for (fid, tid), w in self._edge_weights.items()
            ],
            key=lambda e: e["weight"],
            reverse=True
        )[:50]

        # Platform stats
        platform_stats = {}
        for platform in platforms:
            platform_nodes = [n for n in self._nodes.values() if platform in n.platforms]
            if platform_nodes:
                platform_stats[platform] = {
                    "agent_count": len(platform_nodes),
                    "top_influencer": max(platform_nodes, key=lambda n: n.influence_score).to_dict()
                    if platform_nodes else None,
                }

        result = {
            "analyzed_at": datetime.now().isoformat(),
            "total_agents": len(self._nodes),
            "total_actions": len(all_actions),
            "total_posts_tracked": len(self._post_registry),
            "top_influencers": top_influencers,
            "influence_network": top_edges,
            "platform_stats": platform_stats,
        }

        # Cache to disk
        output_path = os.path.join(self.simulation_dir, "influence_report.json")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Influence report saved: {output_path}")
        except Exception as e:
            logger.warning(f"Failed to save influence report: {e}")

        return result


def get_influence_report(simulation_id: str) -> Dict[str, Any]:
    """
    Get influence analysis for a simulation.
    Returns cached report if available, otherwise runs analysis.
    """
    simulation_dir = os.path.join(Config.OASIS_SIMULATION_DATA_DIR, simulation_id)
    if not os.path.exists(simulation_dir):
        return {"success": False, "error": "Simulation directory not found"}

    # Check for cached report
    cached_path = os.path.join(simulation_dir, "influence_report.json")
    if os.path.exists(cached_path):
        try:
            with open(cached_path, "r", encoding="utf-8") as f:
                return {"success": True, "data": json.load(f), "cached": True}
        except Exception:
            pass

    # Run fresh analysis
    try:
        service = InfluenceAttributionService(simulation_dir)
        result = service.analyze()
        return {"success": True, "data": result, "cached": False}
    except Exception as e:
        logger.error(f"Influence analysis failed: {e}")
        return {"success": False, "error": str(e)}
