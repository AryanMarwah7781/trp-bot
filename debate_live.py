#!/usr/bin/env python3
"""
TRP Bot - Live AI Pundit Debate System
Real-time debate generation using MiniMax API

Integrates with the existing debate.py prompts but generates
actual AI responses using MiniMax API.
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional

# Import from existing debate.py
from debate import PERSONAS, DEBATE_CONTEXT, generate_prompt_for_persona

# MiniMax API Configuration
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

# Default model - can be overridden
DEFAULT_MODEL = "MiniMax-M2.1"


class MiniMaxClient:
    """Client for interacting with MiniMax API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or MINIMAX_API_KEY
        self.base_url = MINIMAX_BASE_URL
        
    def chat_completion(
        self, 
        messages: List[Dict], 
        model: str = DEFAULT_MODEL,
        temperature: float = 0.8,
        max_tokens: int = 500
    ) -> Optional[str]:
        """Generate chat completion from MiniMax API"""
        
        if not self.api_key:
            print("⚠️  No MiniMax API key configured")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/text/chatcompletion_v2",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ API timeout")
            return None
        except Exception as e:
            print(f"❌ API error: {e}")
            return None


def generate_persona_response(
    client: MiniMaxClient,
    persona_id: str,
    context: Dict,
    other_responses: List[Dict] = None,
    temperature: float = 0.9
) -> Optional[str]:
    """
    Generate a response for a specific persona using MiniMax API.
    
    Args:
        client: MiniMax API client
        persona_id: Which persona (roy, gary, jamie)
        context: Debate context (matches, stories, etc.)
        other_responses: Previous responses to react to
        temperature: Creativity level (higher = more creative)
    
    Returns:
        Generated response text or None if failed
    """
    
    # Generate the prompt using existing debate.py logic
    prompt = generate_prompt_for_persona(persona_id, context, other_responses)
    
    # Format for MiniMax chat API
    messages = [
        {
            "role": "system",
            "content": f"""You are {PERSONAS[persona_id]['name']}, a Premier League football pundit on a popular UK sports show.

Your personality: {PERSONAS[persona_id]['style']}
Your voice: {PERSONAS[persona_id]['voice']}

You speak naturally, like you're on TV or a podcast. Keep responses conversational and engaging.
- Don't use bullet points or lists
- React to what others say if applicable
- Be passionate and entertaining
- Keep responses to about 60-90 seconds of speech (roughly 100-150 words)
- Don't be overly formal"""
        },
        {
            "role": "user", 
            "content": prompt
        }
    ]
    
    print(f"🎤 Generating response for {persona_id.upper()}...")
    
    response = client.chat_completion(
        messages=messages,
        temperature=temperature,
        max_tokens=300
    )
    
    return response


def run_debate_round(
    client: MiniMaxClient,
    context: Dict,
    round_num: int = 1,
    persona_order: List[str] = None
) -> List[Dict]:
    """
    Run a single round of debate where each persona responds.
    
    Args:
        client: MiniMax API client
        context: Debate context
        round_num: Which round this is
        persona_order: Order of personas to speak
    
    Returns:
        List of response dicts with persona, round, and response text
    """
    
    if persona_order is None:
        persona_order = ["roy", "gary", "jamie"]
    
    responses = []
    
    print(f"\n{'='*60}")
    print(f"📺 DEBATE ROUND {round_num}")
    print(f"{'='*60}")
    
    for persona_id in persona_order:
        print(f"\n👤 {PERSONAS[persona_id]['name'].upper()} is thinking...")
        
        # Get previous responses from this round to react to
        prev_responses = [
            {"persona": r["persona"], "response": r["response"]}
            for r in responses if r.get("round") == round_num and r.get("response")
        ]
        
        # Generate response
        response_text = generate_persona_response(
            client=client,
            persona_id=persona_id,
            context=context,
            other_responses=prev_responses if prev_responses else None,
            temperature=0.9  # Higher temperature for more personality
        )
        
        if response_text:
            print(f"   ✅ Got response ({len(response_text)} chars)")
            
            response_data = {
                "persona": persona_id,
                "persona_name": PERSONAS[persona_id]["name"],
                "round": round_num,
                "response": response_text,
                "timestamp": datetime.now().isoformat()
            }
            responses.append(response_data)
            
            # Print the response
            print(f"\n💬 {PERSONAS[persona_id]['name']}:")
            print(f"   \"{response_text}\"")
        else:
            print(f"   ❌ Failed to generate response")
            responses.append({
                "persona": persona_id,
                "persona_name": PERSONAS[persona_id]["name"],
                "round": round_num,
                "response": None,
                "error": "Failed to generate",
                "timestamp": datetime.now().isoformat()
            })
    
    return responses


def run_full_debate(
    client: MiniMaxClient,
    context: Dict,
    rounds: int = 2
) -> Dict:
    """
    Run a full debate with multiple rounds.
    
    Args:
        client: MiniMax API client
        context: Debate context
        rounds: Number of debate rounds
    
    Returns:
        Full debate result with all responses
    """
    
    print("\n" + "🎬" * 20)
    print("🏆 LIVE EPL DEBATE - Powered by MiniMax AI")
    print("🎬" * 20)
    print(f"\nWeek: {context.get('week', 'Current')}")
    print(f"Topics: {', '.join(context.get('top_stories', [])[:3])}")
    print(f"\nStarting {rounds} rounds of debate...\n")
    
    all_responses = []
    
    for round_num in range(1, rounds + 1):
        round_responses = run_debate_round(
            client=client,
            context=context,
            round_num=round_num
        )
        all_responses.extend(round_responses)
        
        # Brief pause between rounds
        if round_num < rounds:
            print(f"\n⏳ Brief pause before next round...")
    
    # Compile results
    result = {
        "context": context,
        "rounds": rounds,
        "generated_at": datetime.now().isoformat(),
        "responses": all_responses,
        "summary": {
            "total_responses": len([r for r in all_responses if r.get("response")]),
            "failed_responses": len([r for r in all_responses if not r.get("response")])
        }
    }
    
    print(f"\n{'='*60}")
    print("📊 DEBATE COMPLETE")
    print(f"{'='*60}")
    print(f"Total responses: {result['summary']['total_responses']}")
    print(f"Failed: {result['summary']['failed_responses']}")
    
    return result


def save_debate(result: Dict, filename: str = None) -> str:
    """Save debate result to JSON file"""
    if filename is None:
        filename = f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"💾 Saved to {filename}")
    return filename


def load_context_from_file(filepath: str) -> Dict:
    """Load debate context from a JSON file"""
    with open(filepath, "r") as f:
        return json.load(f)


def demo_with_sample_context():
    """Run a demo debate with sample context"""
    
    # Check for API key
    if not MINIMAX_API_KEY:
        print("⚠️  MINIMAX_API_KEY not set!")
        print("   Set it with: export MINIMAX_API_KEY='your-key'")
        print("\n   Demo will use placeholder responses...")
    
    # Initialize client
    client = MiniMaxClient()
    
    # Sample context
    context = {
        "week": "Feb 10-16, 2026",
        "top_stories": [
            "Arsenal title charge stuttering after Brentford draw",
            "Liverpool beat Man City in huge Anfield clash",
            "Cole Palmer scoring every week - is he world class now?",
            "VAR drama as Tottenham lose controversial points"
        ],
        "matches": [
            {"home": "Arsenal", "away": "Brentford", "score": "1-1"},
            {"home": "Liverpool", "away": "Man City", "score": "2-1"},
            {"home": "Chelsea", "away": "West Ham", "score": "3-1"},
        ]
    }
    
    # Run 2 rounds of debate
    result = run_full_debate(client, context, rounds=2)
    
    # Save result
    save_debate(result)
    
    return result


if __name__ == "__main__":
    # Run demo
    demo_with_sample_context()
