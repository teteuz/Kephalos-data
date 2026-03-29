from pathlib import Path
files = [
 Path(r'C:/Users/mathe/MiroFish/frontend/src/components/Step4Report.vue'),
 Path(r'C:/Users/mathe/MiroFish/frontend/src/components/Step5Interaction.vue'),
 Path(r'C:/Users/mathe/MiroFish/frontend/src/components/HistoryDatabase.vue'),
 Path(r'C:/Users/mathe/MiroFish/frontend/src/App.vue'),
]
repl = {
 '与模拟items体对话，了解他们的观点':'Chat with simulated individuals to understand their perspectives',
 '请先选择一items模拟items体':'Please select a simulated individual first',
 'No response数据':'No response data',
 'Send survey给':'Send survey to',
 'items对象':'targets',
 '问卷Send failed':'Survey send failed',
 '加载报告数据':'Loading report data',
 '报告数据加载完成':'Report data loaded successfully',
 'items模拟items体':'simulated individuals',
 '加载模拟items体失败':'Failed to load simulated individuals',
 '与 Step5「Deep Interaction」must be started while running and do not support historical replay':'and Step5 "Deep Interaction" must be started while running and do not support historical replay',
 'Step3「Start Simulation」':'Step3 "Start Simulation" ',
 '/* 全局样式重置 */':'/* Global reset */',
 '预测场景: ':'Scenario: ',
 '当前关键记忆':'Current Key Memory',
 '核心实体':'Core Entities',
 '关系链':'Relationship Chains',
 '子问题':'Sub-questions',
 '时序记忆中所关联的最新关键事实':'Latest key facts linked to temporal memory',
 '共 ':'Total ',
 ' 条':' items',
 '收起 ▲':'Collapse ▲',
 '展开全部 ':'Expand all ',
 ' 个':' items',
 '漂移查询生成分析子问题':'Drift-query generated sub-questions',
 '暂None当前关键记忆':'No current key memory',
 '暂None核心实体':'No core entities',
 '暂None关系链':'No relationship chains',
 '当前有效记忆':'Current valid memory',
 '历史记忆':'Historical memory',
 '涉及实体':'Involved entities',
 '暂None当前有效记忆':'No current valid memory',
 '暂None历史记忆':'No historical memory',
 '暂None涉及实体':'No involved entities',
 '[None回复]':'[No response]'
}
for p in files:
    s = p.read_text(encoding='utf-8')
    for k,v in repl.items():
        s = s.replace(k,v)
    p.write_text(s,encoding='utf-8')
print('ok')
