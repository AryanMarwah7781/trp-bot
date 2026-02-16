# TRP Bot - Live AI Pundit Debate System
# Multiple AI agents debating EPL topics in real-time

import json
from datetime import datetime

# Persona definitions
PERSONAS = {
    "roy": {
        "name": "Roy",
        "style": "aggressive, passionate, short-tempered, says it like it is",
        "voice": "authoritative British male",
        "favorite_team": None,  # Neutral but hates soft players
    },
    "gary": {
        "name": "Gary", 
        "style": "calm, tactical, analytical, explains the game well",
        "voice": "measured British male", 
        "favorite_team": "Manchester United",
    },
    "jamie": {
        "name": "Jamie",
        "style": "funny, memes, entertainment, loud personality",
        "voice": "energetic British male",
        "favorite_team": "Liverpool",
    }
}

# Sample context for debate
DEBATE_CONTEXT = {
    "week": "Feb 7-13, 2026",
    "top_stories": [
        "Arsenal dropped points against Brentford",
        "Liverpool beat Man City at Anfield",
        "Palmer continuing his incredible form",
        "VAR controversy in Tottenham match"
    ],
    "matches": [
        {"home": "Arsenal", "away": "Brentford", "score": "1-1"},
        {"home": "Liverpool", "away": "Man City", "score": "2-1"},
    ]
}

def generate_prompt_for_persona(persona_id, context, other_responses=None):
    """Generate prompt for a specific persona"""
    
    persona = PERSONAS[persona_id]
    
    prompt = f"""You are {persona['name']}, a Premier League pundit.

Your style: {persona['style']}
Your voice: {persona['voice']}

Current context:
- Top stories this week: {', '.join(context.get('top_stories', []))}
- Recent matches: {context.get('matches', [])}

"""
    
    if other_responses:
        prompt += f"\nOther pundits said:\n"
        for resp in other_responses:
            prompt += f"- {resp['persona']}: {resp['response'][:200]}...\n"
        prompt += "\nNow respond to what the others said. Keep it under 60 seconds of speech (~150 words). Be natural, reactive, add your opinion."
    else:
        prompt += "\nStart the debate! Pick the most interesting topic and give your hot take. Keep it under 60 seconds of speech (~150 words)."
    
    return prompt

def generate_debate_round(context, round_num=1):
    """Generate one round of debate"""
    
    responses = []
    
    # Round 1: Each persona gives their initial take
    for persona_id in ["roy", "gary", "jamie"]:
        prompt = generate_prompt_for_persona(persona_id, context, None)
        # Here we'd call the AI - for now just show the prompt
        print(f"\n=== {persona_id.upper()} ===")
        print(prompt[:500])
        responses.append({
            "persona": persona_id,
            "prompt": prompt
        })
    
    return responses

def generate_debate(context, rounds=2):
    """Generate full debate with multiple rounds"""
    
    print("=" * 60)
    print("LIVE EPL DEBATE")
    print("=" * 60)
    print(f"Week: {context.get('week')}")
    print()
    
    all_responses = []
    
    for round_num in range(1, rounds + 1):
        print(f"\n--- Round {round_num} ---")
        
        # Each persona responds
        for i, persona_id in enumerate(["roy", "gary", "jamie"]):
            # Previous responses from this round
            prev_responses = [
                {"persona": p["persona"], "response": p.get("response", "")}
                for p in all_responses if p.get("round") == round_num
            ]
            
            prompt = generate_prompt_for_persona(persona_id, context, prev_responses)
            
            print(f"\n🤔 {persona_id.upper()} is thinking...")
            
            # In production, this is where we'd call the AI API
            # For now, just show what the prompt would be
            
            response = {
                "persona": persona_id,
                "round": round_num,
                "prompt": prompt,
                # In production: "response": call_ai_api(prompt)
            }
            
            all_responses.append(response)
    
    return all_responses

if __name__ == "__main__":
    # Test with sample context
    print("Testing debate generator...")
    generate_debate(DEBATE_CONTEXT, rounds=2)
