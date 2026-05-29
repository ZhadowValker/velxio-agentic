# 🤖 SoundMind Agent User Guide

The SoundMind Agent is a professional embedded hardware engineering assistant. It doesn't just write code; it designs and verifies physical circuitry.

## 🛠️ Core Capabilities
- **Autonomous Synthesis:** Can design circuits from a high-level description (e.g., "Build a weather station with an ESP32 and DHT22").
- **Closed-Loop Verification:** The agent uses the `analyze_circuit_pins` tool to ensure there are no electrical shorts before it suggests a final solution.
- **Auto-Correction:** If a compilation error or simulation failure occurs, the agent will identify the root cause and apply a patch automatically.

## 🚀 How to interact
### 1. Design Requests
To get the best results, be specific about the hardware.
*Good:* "Create a circuit with an Arduino Uno, a 220 ohm resistor, and a red LED on pin 13. Write a blink sketch."
*Agentic Flow:* Plan $\rightarrow$ Wire $\rightarrow$ Code $\rightarrow$ Verify $\rightarrow$ Result.

### 2. Debugging
If the simulation isn't behaving as expected, simply tell the agent:
"The LED isn't blinking, check the wiring and the serial output."
The agent will enter the **Verification Loop**, check the pin maps, and fix the topology.

## ⚙️ Internal Protocol
The agent follows a strict sequence:
1. **Sensing:** `get_project_outline` $\rightarrow$ `get_canvas_spatial_context`.
2. **Planning:** Connection Table Generation.
3. **Synthesis:** `add_component_batch` $\rightarrow$ `connect_pins_batch`.
4. **Execution:** `generate_code_files` $\rightarrow$ `compile_project`.
5. **Verification:** `analyze_circuit_pins` $\rightarrow$ `validate_circuit_logic`.
