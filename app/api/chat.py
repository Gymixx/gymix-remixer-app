import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies.auth import AuthDep

router = APIRouter(prefix="/api/chat", tags=["AI Chat"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Smart fallback answers for fitness questions
def get_fitness_reply(message: str) -> str:
    msg = message.lower()
    if "hip thrust" in msg:
        return ("To do a hip thrust: Sit on the floor with your upper back against a bench. "
                "Place a barbell or weight across your hips, then drive through your heels to lift your hips upward. "
                "Squeeze your glutes at the top, then lower slowly. Keep your chin tucked and core braced.")
    elif "ab crunch" in msg or "crunch" in msg:
        return ("For an ab crunch: Lie on your back with knees bent, feet flat. Place your hands behind your head (don't pull). "
                "Engage your core and lift your shoulder blades off the floor, crunching upward. Lower slowly with control.")
    elif "push up" in msg or "pushup" in msg:
        return ("Push-up: Start in a high plank, hands shoulder-width apart. Lower your chest toward the floor by bending elbows at 45°, "
                "keeping your body straight. Push back up through your palms. Modify by dropping knees if needed.")
    elif "squat" in msg:
        return ("Squat: Stand with feet shoulder-width. Keep your chest up, push hips back as if sitting into a chair. "
                "Go as low as comfortable, then drive through heels to stand. Keep knees aligned with toes.")
    elif "bicep curl" in msg:
        return ("Bicep curl: Hold dumbbells at your sides, palms facing forward. Keeping elbows pinned to your sides, "
                "curl the weights up toward your shoulders, then lower under control.")
    elif "diet" in msg or "nutrition" in msg:
        return ("For fitness, aim for a balanced diet: lean proteins (chicken, fish, tofu), complex carbs (oats, sweet potatoes), "
                "healthy fats (avocado, nuts), and plenty of vegetables. Stay hydrated and adjust calories based on your goals.")
    elif "workout routine" in msg or "plan" in msg:
        return ("A good beginner routine: 3-4 days per week of full-body workouts including squats, push-ups, rows, and planks. "
                "Add 10-15 min cardio. Rest days are important. Increase intensity gradually.")
    else:
        return ("I'm your fitness assistant. Ask me how to do specific exercises (e.g., 'hip thrust', 'push-up'), "
                "about nutrition, or creating a workout plan. I'm here to help!")

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, user: AuthDep):
    api_key = "sk-59addf63a8bd464c92242421db666aa1"
    base_url = "https://ai-gen.sundaebytestt.com"
    model = "meta/llama-3.2-3b-instruct"
    
    # Possible endpoints to try
    endpoints = [
        "/v1/chat/completions",
        "/v1/completions",
        "/generate",
        "/api/generate",
        "/completions"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            try:
                logger.info(f"Trying endpoint: {url}")
                
                # Prepare payload based on endpoint type
                if "chat/completions" in endpoint:
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": request.message}],
                        "max_tokens": 300,
                        "temperature": 0.7
                    }
                elif "completions" in endpoint and "chat" not in endpoint:
                    prompt = f"Question: {request.message}\nAnswer:"
                    payload = {
                        "model": model,
                        "prompt": prompt,
                        "max_tokens": 300,
                        "temperature": 0.7
                    }
                else:  # /generate or similar
                    payload = {
                        "inputs": request.message,
                        "parameters": {"max_new_tokens": 300, "temperature": 0.7}
                    }
                
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Extract reply from various response formats
                    reply = None
                    if "choices" in data:
                        if "message" in data["choices"][0]:
                            reply = data["choices"][0]["message"]["content"]
                        elif "text" in data["choices"][0]:
                            reply = data["choices"][0]["text"]
                    elif "generated_text" in data:
                        reply = data["generated_text"]
                    elif "response" in data:
                        reply = data["response"]
                    if reply:
                        logger.info(f"Success with endpoint {endpoint}")
                        return ChatResponse(reply=reply.strip())
            except Exception as e:
                logger.warning(f"Endpoint {endpoint} failed: {str(e)}")
                continue
    
    # Fallback: use smart mock responses
    logger.info("All API endpoints failed, using fallback fitness answers")
    fallback_reply = get_fitness_reply(request.message)
    return ChatResponse(reply=fallback_reply)