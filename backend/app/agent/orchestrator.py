\"\"\"
SoundMind Agent Orchestrator

This module implements the iterative 'Plan-Execute-Verify' loop.
It coordinates between the LLM Agent, the MCP Server tools, and 
the Simulation Engine to ensure hardware designs are logically sound.
\"\"\"

from __future__ import annotations
import asyncio
import logging
from typing import Any, Optional, Dict, List
from app.agent.schemas import ProjectSnapshotV2

logger = logging.getLogger(__name__)

class SoundMindOrchestrator:
    def __init__(self, agent, mcp_server):
        self.agent = agent
        self.mcp = mcp_server
        self.current_circuit: Optional[dict] = None

    async def run_design_cycle(self, user_request: str, snapshot: ProjectSnapshotV2):
        \"\"\"
        The Core Agentic Loop:
        1. Analysis: Use LLM to plan the circuit.
        2. Synthesis: Use MCP tools to create/update the circuit.
        3. Verification: Use MCP tools to analyze pins and logic.
        4. Iteration: If verification fails, feed errors back to LLM and repeat.
        \"\"\"
        
        # 1. Plan
        plan_response = await self._generate_design_plan(user_request, snapshot)
        
        # 2. Execute (Synthesis)
        circuit = await self._execute_design_plan(plan_response)
        self.current_circuit = circuit
        
        # 3. Verify (The 'Eyes')
        verification_result = await self._verify_hardware(circuit)
        
        if verification_result.get(\"status\") == \"PASS\":
            return {
                \"success\": True, 
                \"circuit\": circuit, 
                \"log\": \"Hardware verified: All checks passed.\",
                \"verification_data\": verification_result.get(\"data\")
            }
        else:
            # 4. Iterate (Auto-Correction) - Attempt one loop of self-correction
            logger.warning(f\"Verification failed: {verification_result.get('reason')}. Attempting auto-correction...\")
            return await self._iterate_design(user_request, circuit, verification_result)

    async def _generate_design_plan(self, request: str, snapshot: ProjectSnapshotV2) -> Dict[str, Any]:
        \"\"\"
        Prompts the agent to analyze the request and produce a structured connection table
        and component list before any tools are called.
        \"\"\"
        prompt = (
            f\"Analyze this hardware request: '{request}'.\\n\"
            f\"Current Project State: {snapshot}\\n\"
            \"Produce a detailed design plan including:\\n\"
            \"1. List of required components.\\n\"
            \"2. A pin-to-pin mapping table.\\n\"
            \"3. Justification for the choice of pins.\\n\"
            \"Format the output as a JSON-like structure for synthesis.\"
        )
        return await self.agent.call(prompt)

    async def _execute_design_plan(self, plan: Any) -> Dict[str, Any]:
        \"\"\"
        Translates the plan into actual circuit objects using MCP tools.
        \"\"\"
        execution_prompt = (
            f\"Based on this plan: {plan}, use the 'create_circuit' or 'update_circuit' \"
            \"tools to implement the hardware design exactly. return the final circuit object.\"
        )
        result = await self.agent.call(execution_prompt)
        
        if isinstance(result, dict) and \"components\" in result:
            return result
        
        return {\"error\": \"Agent failed to return a valid circuit object during synthesis.\" }

    async def _verify_hardware(self, circuit: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        The critical 'Verification' gate. Uses MCP diagnostics to check for illegal states.
        \"\"\"
        if not circuit or \"error\" in circuit:
            return {\"status\": \"FAIL\", \"reason\": \"Invalid circuit provided for verification.\" }

        # Parallel check of pins and logic
        pins_task = self.mcp.analyze_circuit_pins(circuit)
        logic_task = self.mcp.validate_circuit_logic(circuit)
        
        pins, logic = await asyncio.gather(pins_task, logic_task)

        pin_map = pins.get(\"pin_map\", {})
        conflict_found = False
        details = []

        for pin, connected in pin_map.items():
            if len(connected) > 2:
                conflict_found = True
                details.append(f\"Pin {pin} has too many connections: {connected}\")

        if conflict_found:
            return {\"status\": \"FAIL\", \"reason\": \"Pin conflict detected\", \"data\": details}

        if \"FAIL\" in str(logic).upper():
            return {\"status\": \"FAIL\", \"reason\": \"Logic validation failed\", \"data\": logic}

        return {\"status\": \"PASS\", \"data\": f\"Pin verification and logic check successful. {logic}\"}

    async def _iterate_design(self, request: str, circuit: Dict[str, Any], error: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Feeds the verification error back to the agent to perform a targeted patch.
        \"\"\"
        correction_prompt = (
            f\"The hardware design for '{request}' failed verification.\\n\"
            f\"Error: {error.get('reason')}\\n\"
            f\"Details: {error.get('data')}\\n\"
            f\"Current Circuit: {circuit}\\n\"
            \"Identify the mistake and use 'update_circuit' to fix it. Return the corrected circuit object.\"
        )
        
        corrected_circuit = await self.agent.call(correction_prompt)

        if isinstance(corrected_circuit, dict) and \"components\" in corrected_circuit:
            final_verify = await self._verify_hardware(corrected_circuit)
            if final_verify.get(\"status\") == \"PASS\":
                return {\"success\": True, \"circuit\": corrected_circuit, \"log\": \"Auto-corrected and verified.\"}

        return {
            \"success\": False, 
            \"circuit\": circuit,
            \"log\": f\"Auto-correction failed. Manual intervention required: {error.get('reason')}\"
        }
