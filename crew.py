from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter

server_params = {
    "url": "http://localhost:8000/sse", # Replace with your actual SSE server URL
    "transport": "sse" 
}

# Using MCPServerAdapter with a context manager
try:
    with MCPServerAdapter(server_params) as tools:
        print(f"Available tools from SSE MCP server: {[tool.name for tool in tools]}")

        # Example: Using calculator tools from the SSE MCP server
        calculator_agent = Agent(
            role="Mathematical Calculator",
            goal="Perform mathematical calculations using the MCP calculator server tools.",
            backstory="An AI agent specialized in performing arithmetic operations through remote calculator tools. Can add, subtract, multiply, and divide numbers accurately.",
            tools=tools,
            reasoning=True,
            verbose=True,
        )

        calculator_task = Task(
            description="""
            Perform the following calculations using the available calculator tools:
            1. Add 15 and 27
            2. Subtract 10 from 50
            3. Multiply 8 by 6
            4. Divide 100 by 4
            
            Report all results clearly.
            """,
            expected_output="A detailed report showing the results of all four mathematical operations with clear explanations.",
            agent=calculator_agent,
            markdown=True
        )

        calculator_crew = Crew(
            agents=[calculator_agent],
            tasks=[calculator_task],
            verbose=True,
            process=Process.sequential
        )
        
        if tools: # Only kickoff if tools were loaded
            result = calculator_crew.kickoff()
            print("\nCalculator Crew Task Result:\n", result)
        else:
            print("Skipping crew kickoff as tools were not loaded (check server connection).")

except Exception as e:
    print(f"Error connecting to or using Calculator MCP server: {e}")
    print("Ensure the MCP Calculator server is running and accessible at http://localhost:8000/sse")