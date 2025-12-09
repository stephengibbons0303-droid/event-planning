import os
from crewai import Agent, Crew, Task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from models import VenueDetails

os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# Agents
venue_coordinator = Agent(
    role="Venue Coordinator",
    goal="Identify and book an appropriate venue based on event requirements",
    tools=[search_tool, scrape_tool],
    verbose=True,
    backstory="With a keen sense of space and understanding of event logistics, you excel at finding and securing the perfect venue."
)

logistics_manager = Agent(
    role="Logistics Manager",
    goal="Manage all logistics for the event including catering and equipment",
    tools=[search_tool, scrape_tool],
    verbose=True,
    backstory="Organized and detail-oriented, you ensure every logistical aspect is flawlessly executed."
)

marketing_agent = Agent(
    role="Marketing and Communications Agent",
    goal="Effectively market the event and communicate with participants",
    tools=[search_tool, scrape_tool],
    verbose=True,
    backstory="Creative and communicative, you craft compelling messages to maximize event exposure."
)

# Tasks
venue_task = Task(
    description="Find a venue in {event_city} that meets criteria for {event_topic}.",
    expected_output="All the details of a specifically chosen venue.",
    output_json=VenueDetails,
    agent=venue_coordinator
)

logistics_task = Task(
    description="Coordinate catering and equipment for an event with {expected_participants} participants on {tentative_date}.",
    expected_output="Confirmation of all logistics arrangements.",
    async_execution=True,
    agent=logistics_manager
)

marketing_task = Task(
    description="Promote the {event_topic} aiming to engage at least {expected_participants} potential attendees.",
    expected_output="Report on marketing activities and attendee engagement.",
    async_execution=True,
    agent=marketing_agent
)

# Crew
event_crew = Crew(
    agents=[venue_coordinator, logistics_manager, marketing_agent],
    tasks=[venue_task, logistics_task, marketing_task],
    verbose=True
)

def run_crew(event_details):
    return event_crew.kickoff(inputs=event_details)
