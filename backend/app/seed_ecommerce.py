import asyncio
from app.services.project_service import project_service
from app.agent.summit_adapter import summit_adapter

async def main():
    proj = project_service.create_project("Ecommerce App", template="blank")
    print(f"Created project: {proj.id}")
    prompt = "Create an E-Commerce API with product catalog, cart management, and checkout in app.py with pytest tests in tests/test_ecommerce.py"
    await summit_adapter.run_session(proj.id, prompt, user_id="user_a", user_name="Alice (Dev A)")
    print("Completed E-Commerce App creation!")

if __name__ == "__main__":
    asyncio.run(main())
