"""
OASIS Agent Profile Generator
Converts Zep graph entities into Agent Profile format for the OASIS simulation platform.
"""

import json
import random
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from openai import OpenAI
from zep_cloud.client import Zep

from ..config import Config
from ..utils.logger import get_logger
from .zep_entity_reader import EntityNode, ZepEntityReader

logger = get_logger('kephalosdata.oasis_profile')


@dataclass
class OasisAgentProfile:
    """OASIS Agent Profile data structure"""
    user_id: int
    user_name: str
    name: str
    bio: str
    persona: str
    karma: int = 1000
    friend_count: int = 100
    follower_count: int = 150
    statuses_count: int = 500
    age: Optional[int] = None
    gender: Optional[str] = None
    mbti: Optional[str] = None
    country: Optional[str] = None
    profession: Optional[str] = None
    interested_topics: List[str] = field(default_factory=list)
    emotional_baseline: Dict[str, float] = field(default_factory=lambda: {
        "valence": 0.5, "anxiety": 0.3, "trust": 0.6, "excitability": 0.4
    })
    cognitive_biases: List[str] = field(default_factory=list)
    socioeconomic_tier: str = "medium"
    source_entity_uuid: Optional[str] = None
    source_entity_type: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def to_reddit_format(self) -> Dict[str, Any]:
        profile = {
            "user_id": self.user_id,
            "username": self.user_name,
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "karma": self.karma,
            "created_at": self.created_at,
        }
        if self.age:
            profile["age"] = self.age
        if self.gender:
            profile["gender"] = self.gender
        if self.mbti:
            profile["mbti"] = self.mbti
        if self.country:
            profile["country"] = self.country
        if self.profession:
            profile["profession"] = self.profession
        if self.interested_topics:
            profile["interested_topics"] = self.interested_topics
        profile["emotional_baseline"] = self.emotional_baseline
        if self.cognitive_biases:
            profile["cognitive_biases"] = self.cognitive_biases
        if self.socioeconomic_tier:
            profile["socioeconomic_tier"] = self.socioeconomic_tier
        return profile

    def to_twitter_format(self) -> Dict[str, Any]:
        profile = {
            "user_id": self.user_id,
            "username": self.user_name,
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "friend_count": self.friend_count,
            "follower_count": self.follower_count,
            "statuses_count": self.statuses_count,
            "created_at": self.created_at,
        }
        if self.age:
            profile["age"] = self.age
        if self.gender:
            profile["gender"] = self.gender
        if self.mbti:
            profile["mbti"] = self.mbti
        if self.country:
            profile["country"] = self.country
        if self.profession:
            profile["profession"] = self.profession
        if self.interested_topics:
            profile["interested_topics"] = self.interested_topics
        profile["emotional_baseline"] = self.emotional_baseline
        if self.cognitive_biases:
            profile["cognitive_biases"] = self.cognitive_biases
        if self.socioeconomic_tier:
            profile["socioeconomic_tier"] = self.socioeconomic_tier
        return profile

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "karma": self.karma,
            "friend_count": self.friend_count,
            "follower_count": self.follower_count,
            "statuses_count": self.statuses_count,
            "age": self.age,
            "gender": self.gender,
            "mbti": self.mbti,
            "country": self.country,
            "profession": self.profession,
            "interested_topics": self.interested_topics,
            "emotional_baseline": self.emotional_baseline,
            "cognitive_biases": self.cognitive_biases,
            "socioeconomic_tier": self.socioeconomic_tier,
            "source_entity_uuid": self.source_entity_uuid,
            "source_entity_type": self.source_entity_type,
            "created_at": self.created_at,
        }


class OasisProfileGenerator:
    """OASIS Profile Generator — converts Zep entities into Agent Profiles."""

    MBTI_TYPES = [
        "INTJ", "INTP", "ENTJ", "ENTP",
        "INFJ", "INFP", "ENFJ", "ENFP",
        "ISTJ", "ISFJ", "ESTJ", "ESFJ",
        "ISTP", "ISFP", "ESTP", "ESFP"
    ]

    COUNTRIES = [
        "China", "US", "UK", "Japan", "Germany", "France",
        "Canada", "Australia", "Brazil", "India", "South Korea"
    ]

    INDIVIDUAL_ENTITY_TYPES = [
        "student", "alumni", "professor", "person", "publicfigure",
        "expert", "faculty", "official", "journalist", "activist"
    ]

    GROUP_ENTITY_TYPES = [
        "university", "governmentagency", "organization", "ngo",
        "mediaoutlet", "company", "institution", "group", "community"
    ]

    def __init__(self, api_key=None, base_url=None, model_name=None, zep_api_key=None, graph_id=None):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model_name = model_name or Config.LLM_MODEL_NAME
        if not self.api_key:
            raise ValueError("LLM_API_KEY not configured")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.zep_api_key = zep_api_key or Config.ZEP_API_KEY
        self.zep_client = None
        self.graph_id = graph_id
        if self.zep_api_key:
            try:
                self.zep_client = Zep(api_key=self.zep_api_key)
            except Exception as e:
                logger.warning(f"Zep client init failed: {e}")

    def generate_profile_from_entity(self, entity, user_id, use_llm=True):
        entity_type = entity.get_entity_type() or "Entity"
        name = entity.name
        user_name = self._generate_username(name)
        context = self._build_entity_context(entity)
        if use_llm:
            profile_data = self._generate_profile_with_llm(name, entity_type, entity.summary, entity.attributes, context)
        else:
            profile_data = self._generate_profile_rule_based(name, entity_type, entity.summary, entity.attributes)
        return OasisAgentProfile(
            user_id=user_id,
            user_name=user_name,
            name=name,
            bio=profile_data.get("bio", f"{entity_type}: {name}"),
            persona=profile_data.get("persona", entity.summary or f"A {entity_type} named {name}."),
            karma=profile_data.get("karma", random.randint(500, 5000)),
            friend_count=profile_data.get("friend_count", random.randint(50, 500)),
            follower_count=profile_data.get("follower_count", random.randint(100, 1000)),
            statuses_count=profile_data.get("statuses_count", random.randint(100, 2000)),
            age=profile_data.get("age"),
            gender=profile_data.get("gender"),
            mbti=profile_data.get("mbti"),
            country=profile_data.get("country"),
            profession=profile_data.get("profession"),
            interested_topics=profile_data.get("interested_topics", []),
            emotional_baseline=profile_data.get("emotional_baseline", {
                "valence": 0.5, "anxiety": 0.3, "trust": 0.6, "excitability": 0.4
            }),
            cognitive_biases=profile_data.get("cognitive_biases", []),
            socioeconomic_tier=profile_data.get("socioeconomic_tier", "medium"),
            source_entity_uuid=entity.uuid,
            source_entity_type=entity_type,
        )

    def _generate_username(self, name):
        username = name.lower().replace(" ", "_")
        username = ''.join(c for c in username if c.isalnum() or c == '_')
        return f"{username}_{random.randint(100, 999)}"

    def _search_zep_for_entity(self, entity):
        import concurrent.futures
        if not self.zep_client:
            return {"facts": [], "node_summaries": [], "context": ""}
        entity_name = entity.name
        results = {"facts": [], "node_summaries": [], "context": ""}
        if not self.graph_id:
            return results
        query = f"All information, activities, events, relationships and background about {entity_name}"

        def search_edges():
            for attempt in range(3):
                try:
                    return self.zep_client.graph.search(query=query, graph_id=self.graph_id, limit=30, scope="edges", reranker="rrf")
                except Exception as e:
                    if attempt < 2:
                        time.sleep(2 ** attempt)
            return None

        def search_nodes():
            for attempt in range(3):
                try:
                    return self.zep_client.graph.search(query=query, graph_id=self.graph_id, limit=20, scope="nodes", reranker="rrf")
                except Exception as e:
                    if attempt < 2:
                        time.sleep(2 ** attempt)
            return None

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                edge_result = executor.submit(search_edges).result(timeout=30)
                node_result = executor.submit(search_nodes).result(timeout=30)
            all_facts = set()
            if edge_result and hasattr(edge_result, 'edges') and edge_result.edges:
                for edge in edge_result.edges:
                    if hasattr(edge, 'fact') and edge.fact:
                        all_facts.add(edge.fact)
            results["facts"] = list(all_facts)
            all_summaries = set()
            if node_result and hasattr(node_result, 'nodes') and node_result.nodes:
                for node in node_result.nodes:
                    if hasattr(node, 'summary') and node.summary:
                        all_summaries.add(node.summary)
                    if hasattr(node, 'name') and node.name and node.name != entity_name:
                        all_summaries.add(f"Related entity: {node.name}")
            results["node_summaries"] = list(all_summaries)
            parts = []
            if results["facts"]:
                parts.append("Facts:\n" + "\n".join(f"- {f}" for f in results["facts"][:20]))
            if results["node_summaries"]:
                parts.append("Related entities:\n" + "\n".join(f"- {s}" for s in results["node_summaries"][:10]))
            results["context"] = "\n\n".join(parts)
        except Exception as e:
            logger.warning(f"Zep search failed ({entity_name}): {e}")
        return results

    def _build_entity_context(self, entity):
        parts = []
        if entity.attributes:
            attrs = [f"- {k}: {v}" for k, v in entity.attributes.items() if v and str(v).strip()]
            if attrs:
                parts.append("### Entity Attributes\n" + "\n".join(attrs))
        existing_facts = set()
        if entity.related_edges:
            rels = []
            for edge in entity.related_edges:
                fact = edge.get("fact", "")
                edge_name = edge.get("edge_name", "")
                direction = edge.get("direction", "")
                if fact:
                    rels.append(f"- {fact}")
                    existing_facts.add(fact)
                elif edge_name:
                    if direction == "outgoing":
                        rels.append(f"- {entity.name} --[{edge_name}]--> (related entity)")
                    else:
                        rels.append(f"- (related entity) --[{edge_name}]--> {entity.name}")
            if rels:
                parts.append("### Related Facts\n" + "\n".join(rels))
        if entity.related_nodes:
            info = []
            for node in entity.related_nodes:
                node_name = node.get("name", "")
                node_summary = node.get("summary", "")
                node_labels = node.get("labels", [])
                custom_labels = [l for l in node_labels if l not in ["Entity", "Node"]]
                label_str = f" ({', '.join(custom_labels)})" if custom_labels else ""
                if node_summary:
                    info.append(f"- **{node_name}**{label_str}: {node_summary}")
                else:
                    info.append(f"- **{node_name}**{label_str}")
            if info:
                parts.append("### Related Entity Info\n" + "\n".join(info))
        zep = self._search_zep_for_entity(entity)
        if zep.get("facts"):
            new_facts = [f for f in zep["facts"] if f not in existing_facts]
            if new_facts:
                parts.append("### Facts from Zep\n" + "\n".join(f"- {f}" for f in new_facts[:15]))
        if zep.get("node_summaries"):
            parts.append("### Nodes from Zep\n" + "\n".join(f"- {s}" for s in zep["node_summaries"][:10]))
        return "\n\n".join(parts)

    def _is_individual_entity(self, entity_type):
        return entity_type.lower() in self.INDIVIDUAL_ENTITY_TYPES

    def _is_group_entity(self, entity_type):
        return entity_type.lower() in self.GROUP_ENTITY_TYPES

    def _generate_profile_with_llm(self, entity_name, entity_type, entity_summary, entity_attributes, context):
        is_individual = self._is_individual_entity(entity_type)
        if is_individual:
            prompt = self._build_individual_persona_prompt(entity_name, entity_type, entity_summary, entity_attributes, context)
        else:
            prompt = self._build_group_persona_prompt(entity_name, entity_type, entity_summary, entity_attributes, context)
        last_error = None
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt(is_individual)},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7 - (attempt * 0.1)
                )
                content = response.choices[0].message.content
                if response.choices[0].finish_reason == 'length':
                    content = self._fix_truncated_json(content)
                try:
                    result = json.loads(content)
                    if not result.get("bio"):
                        result["bio"] = (entity_summary or "")[:200] or f"{entity_type}: {entity_name}"
                    if not result.get("persona"):
                        result["persona"] = entity_summary or f"{entity_name} is a {entity_type}."
                    return result
                except json.JSONDecodeError as je:
                    result = self._try_fix_json(content, entity_name, entity_type, entity_summary)
                    if result.get("_fixed"):
                        del result["_fixed"]
                        return result
                    last_error = je
            except Exception as e:
                last_error = e
                time.sleep(attempt + 1)
        logger.warning(f"LLM failed after 3 attempts: {last_error}, using rule-based")
        return self._generate_profile_rule_based(entity_name, entity_type, entity_summary, entity_attributes)

    def _fix_truncated_json(self, content):
        content = content.strip()
        open_braces = content.count('{') - content.count('}')
        open_brackets = content.count('[') - content.count(']')
        if content and content[-1] not in '",}]':
            content += '"'
        content += ']' * open_brackets
        content += '}' * open_braces
        return content

    def _try_fix_json(self, content, entity_name, entity_type, entity_summary=""):
        import re
        content = self._fix_truncated_json(content)
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            s = match.group()
            def fix_nl(m):
                t = m.group(0).replace('\n', ' ').replace('\r', ' ')
                return re.sub(r'\s+', ' ', t)
            s = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', fix_nl, s)
            try:
                r = json.loads(s)
                r["_fixed"] = True
                return r
            except Exception:
                try:
                    s = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', s)
                    s = re.sub(r'\s+', ' ', s)
                    r = json.loads(s)
                    r["_fixed"] = True
                    return r
                except Exception:
                    pass
        bio_m = re.search(r'"bio"\s*:\s*"([^"]*)"', content)
        per_m = re.search(r'"persona"\s*:\s*"([^"]*)', content)
        bio = bio_m.group(1) if bio_m else ((entity_summary or "")[:200] or f"{entity_type}: {entity_name}")
        persona = per_m.group(1) if per_m else (entity_summary or f"{entity_name} is a {entity_type}.")
        if bio_m or per_m:
            return {"bio": bio, "persona": persona, "_fixed": True}
        return {
            "bio": (entity_summary or "")[:200] or f"{entity_type}: {entity_name}",
            "persona": entity_summary or f"{entity_name} is a {entity_type}."
        }

    def _get_system_prompt(self, is_individual):
        return (
            "You are an expert social media persona generator. "
            "Generate detailed, realistic personas for opinion simulation. "
            "Must return valid JSON. No unescaped newlines in string values. Use English."
        )

    def _build_individual_persona_prompt(self, entity_name, entity_type, entity_summary, entity_attributes, context):
        attrs_str = json.dumps(entity_attributes, ensure_ascii=False) if entity_attributes else "None"
        context_str = (context or "")[:3000] or "No additional context"
        
        # Add diversity based on entity type
        type_specific_instructions = {
            "student": "Focus on academic interests, social activism, and peer interactions. Include study habits and campus life.",
            "alumni": "Emphasize career progression, networking, and giving back to alma mater. Include professional achievements.",
            "professor": "Highlight research expertise, teaching philosophy, and academic collaborations. Include publication history.",
            "expert": "Stress specialized knowledge, consulting work, and thought leadership. Include industry impact.",
            "journalist": "Focus on investigative reporting, news sourcing, and media ethics. Include beat specialization.",
            "activist": "Emphasize social causes, community organizing, and advocacy work. Include movement participation."
        }
        
        type_instruction = type_specific_instructions.get(entity_type.lower(), "Create a realistic social media persona with authentic behaviors and interests.")
        
        return f"""Generate a detailed social media user persona for this entity.

Entity Name: {entity_name}
Entity Type: {entity_type}
Entity Summary: {entity_summary}
Entity Attributes: {attrs_str}

Context:
{context_str}

{type_instruction}

Return JSON with these fields:
1. bio: Social media bio (~200 words) - make it engaging and authentic
2. persona: Detailed persona (~2000 words plain text) including: basic info, background, personality, social media behavior, stance, unique traits, personal memory, communication style, and interaction patterns
3. age: Integer (realistic for the entity type)
4. gender: "male" or "female" (or "other" if not applicable)
5. mbti: MBTI type (choose realistically based on personality traits)
6. country: Country in English (realistic for the entity)
7. profession: Occupation (specific and realistic)
8. interested_topics: Array of 3-8 topics (diverse and relevant)
9. emotional_baseline: Object with these float values (0.0-1.0):
   - valence: overall positive/negative mood baseline (0=very negative, 1=very positive)
   - anxiety: baseline anxiety/stress level (0=calm, 1=highly anxious)
   - trust: baseline trust in institutions and others (0=deeply cynical, 1=very trusting)
   - excitability: tendency to strong emotional reactions (0=stoic, 1=highly reactive)
10. cognitive_biases: Array of 2-4 biases from this list that fit the persona:
    ["confirmation_bias", "authority_bias", "in_group_bias", "availability_bias",
     "recency_bias", "optimism_bias", "negativity_bias", "anchoring_bias",
     "dunning_kruger", "bandwagon_bias", "status_quo_bias", "attribution_bias"]
11. socioeconomic_tier: One of "low", "medium", "high", "very_high" (realistic for entity)

Also incorporate the emotional baseline and cognitive biases into the persona text — describe how the person's emotional tendencies and reasoning patterns affect their online behavior and communication style.

Important: All string values must have no newlines. Use English for all fields. Make the persona highly detailed and realistic.
"""

    def _build_group_persona_prompt(self, entity_name, entity_type, entity_summary, entity_attributes, context):
        attrs_str = json.dumps(entity_attributes, ensure_ascii=False) if entity_attributes else "None"
        context_str = (context or "")[:3000] or "No additional context"
        
        # Add diversity for group entities
        group_instructions = {
            "university": "Focus on academic excellence, research output, student life, and institutional communications. Include alumni network and campus events.",
            "governmentagency": "Emphasize public service, policy announcements, transparency, and official communications. Include regulatory focus and public engagement.",
            "ngo": "Highlight mission-driven work, advocacy campaigns, community impact, and fundraising efforts. Include volunteer coordination and awareness raising.",
            "mediaoutlet": "Focus on editorial standards, news coverage, audience engagement, and journalistic integrity. Include content strategy and media partnerships.",
            "company": "Emphasize corporate values, product/service promotion, industry leadership, and employee culture. Include innovation and market position.",
            "organization": "Focus on organizational goals, member engagement, community building, and collaborative initiatives. Include governance and stakeholder relations."
        }
        
        group_instruction = group_instructions.get(entity_type.lower(), "Create a professional organizational account with authentic communications and engagement patterns.")
        
        return f"""Generate a detailed social media profile for this organization/group entity.

Entity Name: {entity_name}
Entity Type: {entity_type}
Entity Summary: {entity_summary}
Entity Attributes: {attrs_str}

Context:
{context_str}

{group_instruction}

Return JSON with these fields:
1. bio: Official bio (~200 words, professional and engaging)
2. persona: Detailed account profile (~2000 words) including: institution info, account positioning, communication style, content strategy, engagement patterns, stance on issues, operational habits, institutional memory, and stakeholder interactions
3. age: Always 30 (represents established entity)
4. gender: Always "other"
5. mbti: MBTI describing account personality (e.g. ISTJ for formal, ENFJ for engaging)
6. country: Country in English (realistic for the organization)
7. profession: Institutional function/role
8. interested_topics: Array of 3-8 focus areas (relevant to mission)
9. emotional_baseline: Object with these float values (0.0-1.0) representing the account's tone:
   - valence: overall tone positivity (0=very critical/negative, 1=very positive/promotional)
   - anxiety: urgency/alarm tendency (0=calm informational, 1=high urgency)
   - trust: institutional trust projected (0=adversarial, 1=highly cooperative)
   - excitability: responsiveness to events (0=stoic/delayed, 1=rapid reactive)
10. cognitive_biases: Array of 2-3 institutional biases from:
    ["in_group_bias", "authority_bias", "confirmation_bias", "status_quo_bias",
     "optimism_bias", "attribution_bias", "anchoring_bias", "bandwagon_bias"]
11. socioeconomic_tier: One of "medium", "high", "very_high" (institutional level)

Also incorporate the account's emotional tone and institutional biases into the persona description.

Important: All string values must have no newlines. No null values. Use English. Make the profile authentic to the organization's character.
"""

    def _generate_profile_rule_based(self, entity_name, entity_type, entity_summary, entity_attributes):
        t = entity_type.lower()
        if t in ["student", "alumni"]:
            return {
                "bio": f"{entity_type} with interests in academics and social issues.",
                "persona": f"{entity_name} is a {t} actively engaged in academic and social discussions.",
                "age": random.randint(18, 30), "gender": random.choice(["male", "female"]),
                "mbti": random.choice(self.MBTI_TYPES), "country": random.choice(self.COUNTRIES),
                "profession": "Student", "interested_topics": ["Education", "Social Issues", "Technology"],
                "emotional_baseline": {"valence": 0.55, "anxiety": 0.45, "trust": 0.5, "excitability": 0.6},
                "cognitive_biases": ["in_group_bias", "availability_bias"],
                "socioeconomic_tier": "medium",
            }
        elif t in ["publicfigure", "expert", "faculty"]:
            return {
                "bio": "Expert and thought leader in their field.",
                "persona": f"{entity_name} is a recognized {t} sharing insights on important matters.",
                "age": random.randint(35, 60), "gender": random.choice(["male", "female"]),
                "mbti": random.choice(["ENTJ", "INTJ", "ENTP", "INTP"]), "country": random.choice(self.COUNTRIES),
                "profession": entity_attributes.get("occupation", "Expert") if entity_attributes else "Expert",
                "interested_topics": ["Politics", "Economics", "Culture & Society"],
                "emotional_baseline": {"valence": 0.6, "anxiety": 0.25, "trust": 0.55, "excitability": 0.35},
                "cognitive_biases": ["authority_bias", "confirmation_bias"],
                "socioeconomic_tier": "high",
            }
        elif t in ["mediaoutlet", "socialmediaplatform"]:
            return {
                "bio": f"Official account for {entity_name}. News and updates.",
                "persona": f"{entity_name} is a media entity reporting news and facilitating public discourse.",
                "age": 30, "gender": "other", "mbti": "ISTJ", "country": "Unknown",
                "profession": "Media", "interested_topics": ["General News", "Current Events", "Public Affairs"],
                "emotional_baseline": {"valence": 0.5, "anxiety": 0.3, "trust": 0.65, "excitability": 0.5},
                "cognitive_biases": ["status_quo_bias", "authority_bias"],
                "socioeconomic_tier": "high",
            }
        elif t in ["university", "governmentagency", "ngo", "organization"]:
            return {
                "bio": f"Official account of {entity_name}.",
                "persona": f"{entity_name} is an institutional entity that communicates official positions.",
                "age": 30, "gender": "other", "mbti": "ISTJ", "country": "Unknown",
                "profession": entity_type, "interested_topics": ["Public Policy", "Community", "Announcements"],
                "emotional_baseline": {"valence": 0.55, "anxiety": 0.2, "trust": 0.7, "excitability": 0.25},
                "cognitive_biases": ["status_quo_bias", "in_group_bias"],
                "socioeconomic_tier": "very_high",
            }
        else:
            return {
                "bio": (entity_summary or "")[:150] or f"{entity_type}: {entity_name}",
                "persona": entity_summary or f"{entity_name} is a {t} participating in social discussions.",
                "age": random.randint(25, 50), "gender": random.choice(["male", "female"]),
                "mbti": random.choice(self.MBTI_TYPES), "country": random.choice(self.COUNTRIES),
                "profession": entity_type, "interested_topics": ["General", "Social Issues"],
                "emotional_baseline": {"valence": 0.5, "anxiety": 0.35, "trust": 0.5, "excitability": 0.4},
                "cognitive_biases": ["availability_bias"],
                "socioeconomic_tier": "medium",
            }

    def set_graph_id(self, graph_id):
        self.graph_id = graph_id

    def generate_profiles_from_entities(self, entities, use_llm=True, progress_callback=None,
                                         graph_id=None, parallel_count=5, realtime_output_path=None,
                                         output_platform="reddit"):
        import concurrent.futures
        from threading import Lock
        if graph_id:
            self.graph_id = graph_id
        total = len(entities)
        profiles = [None] * total
        completed_count = [0]
        lock = Lock()

        def save_realtime():
            if not realtime_output_path:
                return
            with lock:
                existing = [p for p in profiles if p is not None]
                if not existing:
                    return
                try:
                    if output_platform == "reddit":
                        with open(realtime_output_path, 'w', encoding='utf-8') as f:
                            json.dump([p.to_reddit_format() for p in existing], f, ensure_ascii=False, indent=2)
                    else:
                        import csv
                        data = [p.to_twitter_format() for p in existing]
                        if data:
                            with open(realtime_output_path, 'w', encoding='utf-8', newline='') as f:
                                w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                                w.writeheader()
                                w.writerows(data)
                except Exception as e:
                    logger.warning(f"Real-time save failed: {e}")

        def generate_single(idx, entity):
            entity_type = entity.get_entity_type() or "Entity"
            try:
                profile = self.generate_profile_from_entity(entity=entity, user_id=idx, use_llm=use_llm)
                self._print_generated_profile(entity.name, entity_type, profile)
                return idx, profile, None
            except Exception as e:
                logger.error(f"Failed for entity {entity.name}: {e}")
                fallback = OasisAgentProfile(
                    user_id=idx, user_name=self._generate_username(entity.name),
                    name=entity.name, bio=f"{entity_type}: {entity.name}",
                    persona=entity.summary or "A participant in social discussions.",
                    source_entity_uuid=entity.uuid, source_entity_type=entity_type,
                )
                return idx, fallback, str(e)

        print(f"\n{'='*60}\nStarting generation — {total} entities, parallel: {parallel_count}\n{'='*60}\n")
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_count) as executor:
            futures = {executor.submit(generate_single, idx, e): (idx, e) for idx, e in enumerate(entities)}
            for future in concurrent.futures.as_completed(futures):
                idx, entity = futures[future]
                entity_type = entity.get_entity_type() or "Entity"
                try:
                    ri, profile, error = future.result()
                    profiles[ri] = profile
                    with lock:
                        completed_count[0] += 1
                        current = completed_count[0]
                    save_realtime()
                    if progress_callback:
                        progress_callback(current, total, f"Completed {current}/{total}: {entity.name} ({entity_type})")
                    if error:
                        logger.warning(f"[{current}/{total}] {entity.name} fallback: {error}")
                    else:
                        logger.info(f"[{current}/{total}] OK: {entity.name} ({entity_type})")
                except Exception as e:
                    logger.error(f"Exception processing {entity.name}: {e}")
                    with lock:
                        completed_count[0] += 1
                    profiles[idx] = OasisAgentProfile(
                        user_id=idx, user_name=self._generate_username(entity.name),
                        name=entity.name, bio=f"{entity_type}: {entity.name}",
                        persona=entity.summary or "A participant in social discussions.",
                        source_entity_uuid=entity.uuid, source_entity_type=entity_type,
                    )
                    save_realtime()

        count = len([p for p in profiles if p])
        print(f"\n{'='*60}\nGeneration complete! {count} agents generated\n{'='*60}\n")
        return profiles

    def _print_generated_profile(self, entity_name, entity_type, profile):
        sep = "-" * 70
        topics = ', '.join(profile.interested_topics) if profile.interested_topics else 'None'
        print(f"\n{sep}\n[GENERATED] {entity_name} ({entity_type})\n{sep}")
        print(f"Username: {profile.user_name}\n")
        print(f"[BIO]\n{profile.bio}\n")
        print(f"[PERSONA]\n{profile.persona}\n")
        print(f"Age: {profile.age} | Gender: {profile.gender} | MBTI: {profile.mbti}")
        print(f"Profession: {profile.profession} | Country: {profile.country}")
        print(f"Interests: {topics}\n{sep}")

    def save_profiles(self, profiles, file_path, platform="reddit"):
        if platform == "twitter":
            self._save_twitter_csv(profiles, file_path)
        else:
            self._save_reddit_json(profiles, file_path)

    def _save_twitter_csv(self, profiles, file_path):
        import csv
        if not file_path.endswith('.csv'):
            file_path = file_path.replace('.json', '.csv')
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['user_id', 'name', 'username', 'user_char', 'description'])
            for idx, p in enumerate(profiles):
                uc = f"{p.bio} {p.persona}" if p.persona and p.persona != p.bio else p.bio
                uc = uc.replace('\n', ' ').replace('\r', ' ')
                desc = p.bio.replace('\n', ' ').replace('\r', ' ')
                w.writerow([idx, p.name, p.user_name, uc, desc])
        logger.info(f"Saved {len(profiles)} Twitter profiles to {file_path}")

    def _normalize_gender(self, gender):
        if not gender:
            return "other"
        return {"male": "male", "female": "female", "other": "other"}.get(gender.lower().strip(), "other")

    def _save_reddit_json(self, profiles, file_path):
        data = []
        for idx, p in enumerate(profiles):
            item = {
                "user_id": p.user_id if p.user_id is not None else idx,
                "username": p.user_name, "name": p.name,
                "bio": (p.bio or "")[:150] or p.name,
                "persona": p.persona or f"{p.name} is a participant in social discussions.",
                "karma": p.karma or 1000, "created_at": p.created_at,
                "age": p.age or 30, "gender": self._normalize_gender(p.gender),
                "mbti": p.mbti or "ISTJ", "country": p.country or "Unknown",
            }
            if p.profession:
                item["profession"] = p.profession
            if p.interested_topics:
                item["interested_topics"] = p.interested_topics
            data.append(item)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(profiles)} Reddit profiles to {file_path}")

    def save_profiles_to_json(self, profiles, file_path, platform="reddit"):
        """[Deprecated] Use save_profiles() instead"""
        logger.warning("save_profiles_to_json is deprecated, use save_profiles instead")
        self.save_profiles(profiles, file_path, platform)
