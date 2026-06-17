# -*- coding: utf-8 -*-
"""
Romih Agent - Agent Loop
=========================
Think - Plan - Execute - Observe - Repeat

The brain that transforms Romih from a chatbot into a true agent.
"""
import json
import asyncio
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Step:
    """One step in the execution plan"""
    tool: str
    params: dict
    reasoning: str
    result: str = ""
    success: bool = True


@dataclass  
class ExecutionPlan:
    """Multi-step execution plan"""
    goal: str
    steps: list[Step] = field(default_factory=list)
    current_step: int = 0
    max_steps: int = 5
    complete: bool = False
    final_result: str = ""


class AgentLoop:
    """
    Think - Act - Observe - Repeat
    
    Turns RomihAgent into a genuine autonomous agent.
    """
    
    def __init__(self, agent):
        self.agent = agent
    
    async def execute(self, goal: str) -> str:
        """
        Execute a goal using the agent loop.
        
        1. THINK: Analyze goal, create plan
        2. ACT: Execute tools step by step  
        3. OBSERVE: Check results, adjust if needed
        4. REPEAT: Until done or max steps reached
        """
        # Phase 1: THINK - Plan the approach
        plan = await self._think(goal)
        if not plan.steps:
            return await self._fallback_chat(goal)
        
        # Phase 2-4: ACT - OBSERVE - REPEAT
        results = []
        for i, step in enumerate(plan.steps):
            if i >= plan.max_steps:
                break
            plan.current_step = i
            
            # Execute the tool
            try:
                result = self.agent.tools.execute(
                    step.tool,
                    step.params,
                    auto_approve=step.tool not in ['delete_file', 'run_shell']
                )
                step.result = str(result)[:2000]
                step.success = True
            except Exception as e:
                step.result = f"ERROR: {e}"
                step.success = False
                # Try to recover
                recovery = await self._recover(goal, step, plan)
                if recovery:
                    results.append(recovery)
                    continue
            
            results.append(step.result)
            
            # Check if we have enough
            if self._is_complete(goal, results):
                break
        
        # Phase 5: SYNTHESIZE - Combine results into final answer
        return await self._synthesize(goal, plan, results)
    
    async def _think(self, goal: str) -> ExecutionPlan:
        """Analyze goal and create execution plan using LLM"""
        tools_desc = self._describe_tools()
        
        prompt = f"""You are an AI planner. Given a user goal, create a step-by-step plan using available tools.
Return ONLY valid JSON. No explanation.

Available tools:
{tools_desc}

User goal: {goal}

Return JSON format:
{{"steps": [
  {{"tool": "tool_name", "params": {{"param": "value"}}, "reasoning": "why this step"}}
]}}

Rules:
- Use minimum steps needed (1-3)
- Choose the RIGHT tool for each step
- Only use tools from the list above
- If goal is just a question, return empty steps list []"""
        
        try:
            model_id, provider = await self.agent.router.route(task_type="reasoning")
            messages = [
                {"role": "system", "content": self.agent.system_prompt},
                {"role": "user", "content": prompt}
            ]
            response = await self.agent.openrouter.chat(model_id, messages, 0.1)
            
            # Extract JSON from response
            text = response.content
            # Find JSON block
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            steps = [
                Step(
                    tool=s.get("tool", ""),
                    params=s.get("params", {}),
                    reasoning=s.get("reasoning", "")
                )
                for s in data.get("steps", [])
            ]
            return ExecutionPlan(goal=goal, steps=steps)
        except Exception as e:
            print(f"Planning error: {e}")
            return ExecutionPlan(goal=goal, steps=[])
    
    async def _recover(self, goal: str, failed_step: Step, plan: ExecutionPlan) -> Optional[str]:
        """Try to recover from a failed step"""
        # Simple recovery: try alternative tool or skip
        alternatives = {
            "web_search": "web_fetch",
            "web_fetch": "web_search",
        }
        alt = alternatives.get(failed_step.tool)
        if alt:
            try:
                result = self.agent.tools.execute(alt, failed_step.params, auto_approve=True)
                return str(result)[:2000]
            except:
                pass
        return None
    
    def _is_complete(self, goal: str, results: list) -> bool:
        """Check if we have enough results"""
        return len(results) >= 3  # Max 3 steps per goal
    
    async def _synthesize(self, goal: str, plan: ExecutionPlan, results: list) -> str:
        """Synthesize all results into a final Arabic answer"""
        if not results:
            return await self._fallback_chat(goal)
        
        # Always synthesize via LLM for natural Arabic response
        try:
            model_id, _ = await self.agent.router.route(task_type="arabic")
            steps_summary = "\n".join([
                f"Step {i+1} ({s.tool}): {s.reasoning}\nResult: {r[:500]}"
                for i, (s, r) in enumerate(zip(plan.steps, results))
            ])
            messages = [
                {"role": "system", "content": "You are a helpful Arabic assistant. Convert technical results into a natural, friendly Arabic response. Never output JSON or Python dicts - always natural Arabic."},
                {"role": "user", "content": f"User asked: {goal}\n\nResults from execution:\n{steps_summary}\n\nPlease provide a clear, natural Arabic response telling the user what happened. If it was successful, say so in a friendly way. Show key details."}
            ]
            response = await self.agent.openrouter.chat(model_id, messages, 0.3)
            if response.content and len(response.content.strip()) > 10:
                return response.content
        except Exception as e:
            print(f"Synthesize error: {e}")
        
        # Fallback: format results nicely
        if len(results) == 1:
            r = results[0]
            if isinstance(r, str) and r.startswith("{") and '"ok": true' in r.lower():
                return f"تمت العملية بنجاح ✅"
            return str(r)
        return "\n\n".join([str(r)[:500] for r in results])
    
    async def _fallback_chat(self, goal: str) -> str:
        """Fallback to normal chat if planning fails"""
        return await self.agent.chat(goal)
    
    def _describe_tools(self) -> str:
        """Describe available tools for the planner"""
        lines = []
        # Include ALL tool names for lookup, describe top 50
        all_names = list(self.agent.tools.tools.keys())
        lines.append(f"Available tools ({len(all_names)} total):")
        for name in all_names[:60]:
            tool = self.agent.tools.tools[name]
            params = ", ".join(p.name for p in tool.params)
            lines.append(f"  {name}({params})")
        if len(all_names) > 60:
            lines.append(f"  ... and {len(all_names)-60} more tools")
        return "\n".join(lines)
