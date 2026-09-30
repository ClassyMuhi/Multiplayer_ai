import asyncio
from app.services.project_service import project_service
from app.agent.summit_adapter import summit_adapter

async def main():
    proj = project_service.create_project("Medical App Portal", template="blank")
    print(f"Created project: {proj.id}")
    prompt = "Create a medical app portal website with doctor appointment booking, patient metrics dashboard, index.html, styles.css, app.js, and server.py"
    await summit_adapter.run_session(proj.id, prompt, user_id="user_a", user_name="Alice (Dev A)")
    print("Completed Medical App Website creation!")

if __name__ == "__main__":
    asyncio.run(main())
