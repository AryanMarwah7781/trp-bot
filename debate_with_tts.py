#!/usr/bin/env python3
"""
TRP Bot - Debate with Text-to-Speech
Generates debate and narrates it using available TTS backends.
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from typing import Optional, List

# Import from existing modules
from debate import PERSONAS
from debate_live import (
    MiniMaxClient, 
    run_full_debate, 
    load_context_from_file,
    generate_prompt_for_persona
)


class TTSManager:
    """Manages different TTS backends"""
    
    def __init__(self):
        self.backend = self._detect_backend()
        
    def _detect_backend(self) -> str:
        """Detect available TTS backend"""
        # Check for sherpa-onnx
        sherpa_bin = os.path.expanduser("~/.openclaw/tools/sherpa-onnx-tts/bin/sherpa-onnx-tts")
        if os.path.isfile(sherpa_bin):
            return "sherpa-onnx"
        
        # Check for espeak
        if subprocess.call(["which", "espeak-ng"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            return "espeak"
            
        # Check for festival
        if subprocess.call(["which", "festival"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            return "festival"
        
        # Check for say (macOS)
        if subprocess.call(["which", "say"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            return "say"
        
        return "none"
    
    def speak(self, text: str, voice: str = "default", output_file: str = None) -> bool:
        """Speak text using available backend"""
        print(f"🔊 TTS Backend: {self.backend}")
        
        if self.backend == "none":
            print("⚠️  No TTS backend available!")
            return False
            
        try:
            if self.backend == "sherpa-onnx":
                return self._speak_sherpa(text, output_file)
            elif self.backend == "espeak":
                return self._speak_espeak(text, voice, output_file)
            elif self.backend == "festival":
                return self._speak_festival(text)
            elif self.backend == "say":
                return self._speak_say(text, voice)
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return False
            
        return True
    
    def _speak_sherpa(self, text: str, output_file: str = None) -> bool:
        """Use sherpa-onnx for TTS"""
        sherpa_bin = os.path.expanduser("~/.openclaw/tools/sherpa-onnx-tts/bin/sherpa-onnx-tts")
        model_dir = os.path.expanduser("~/.openclaw/tools/sherpa-onnx-tts/models/vits-piper-en_US-lessac-high")
        
        if output_file:
            cmd = [sherpa_bin, "--model-dir", model_dir, "-o", output_file, text]
        else:
            # Generate temp file and play
            temp_wav = f"/tmp/tts_{datetime.now().timestamp()}.wav"
            cmd = [sherpa_bin, "--model-dir", model_dir, "-o", temp_wav, text]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Sherpa error: {result.stderr}")
                return False
                
            # Play the audio
            subprocess.Popen(["paplay", temp_wav])
            print(f"   Playing: {temp_wav}")
            
        return True
    
    def _speak_espeak(self, text: str, voice: str = "default", output_file: str = None) -> bool:
        """Use espeak for TTS"""
        cmd = ["espeak-ng"]
        
        # Map voices
        voice_map = {
            "roy": "en-uk-north",
            "gary": "en-uk-rp", 
            "jamie": "en-us"
        }
        
        if voice in voice_map:
            cmd.extend(["-v", voice_map[voice]])
            
        if output_file:
            cmd.extend(["-w", output_file])
            
        cmd.append(text)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _speak_festival(self, text: str) -> bool:
        """Use festival for TTS"""
        cmd = ["festival", "--tts"]
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        process.communicate(input=text.encode())
        return process.returncode == 0
    
    def _speak_say(self, text: str, voice: str = "default") -> bool:
        """Use macOS say command"""
        cmd = ["say"]
        
        # macOS voice options
        voice_map = {
            "roy": "Daniel",
            "gary": "Fred", 
            "jamie": "Tom"
        }
        
        if voice in voice_map:
            cmd.extend(["-v", voice_map[voice]])
            
        cmd.append(text)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0


def get_persona_voice(persona_id: str) -> str:
    """Get voice identifier for a persona"""
    voices = {
        "roy": "roy",    # Aggressive, British
        "gary": "gary",  # Calm, analytical
        "jamie": "jamie" # Fun, loud
    }
    return voices.get(persona_id, "default")


def speak_debate_turn(tts: TTSManager, persona_name: str, text: str, delay: float = 0.5):
    """Speak a single debate turn with formatting"""
    print(f"\n🎤 {persona_name}:")
    print(f"   \"{text}\"")
    
    if tts.backend != "none":
        tts.speak(text, voice=get_persona_voice(persona_name.lower()))
    
    # Brief pause between speakers
    import time
    time.sleep(delay)


def run_debate_with_tts(
    client: MiniMaxClient,
    context: dict,
    rounds: int = 2,
    use_tts: bool = True
) -> dict:
    """Run debate with TTS narration"""
    
    tts = TTSManager() if use_tts else None
    
    print("\n" + "="*60)
    print("🏆 LIVE EPL DEBATE - WITH TTS")
    print("="*60)
    
    if use_tts:
        print(f"🔊 TTS Backend: {tts.backend if tts else 'disabled'}")
    
    print(f"\n📅 Week: {context.get('week', 'Current')}")
    print(f"📰 Topics: {', '.join(context.get('top_stories', [])[:3])}")
    print(f"\nStarting {rounds} rounds...\n")
    
    all_responses = []
    
    for round_num in range(1, rounds + 1):
        print(f"\n{'='*60}")
        print(f"📺 ROUND {round_num}")
        print(f"{'='*60}")
        
        # Each persona speaks in order
        for persona_id in ["roy", "gary", "jamie"]:
            persona = PERSONAS[persona_id]
            
            # Get previous responses this round
            prev = [
                {"persona": r["persona"], "response": r.get("response", "")}
                for r in all_responses 
                if r.get("round") == round_num and r.get("response")
            ]
            
            # Generate response
            from debate_live import generate_persona_response
            print(f"\n🤔 {persona['name']} is thinking...")
            
            response_text = generate_persona_response(
                client=client,
                persona_id=persona_id,
                context=context,
                other_responses=prev if prev else None
            )
            
            if response_text:
                response_data = {
                    "persona": persona_id,
                    "persona_name": persona["name"],
                    "round": round_num,
                    "response": response_text,
                    "timestamp": datetime.now().isoformat()
                }
                all_responses.append(response_data)
                
                # Speak it!
                if use_tts:
                    speak_debate_turn(tts, persona["name"], response_text)
                else:
                    print(f"\n🎤 {persona['name']}:")
                    print(f"   \"{response_text}\"")
            else:
                print(f"   ❌ Failed to generate")
                
        # Pause between rounds
        if round_num < rounds:
            print(f"\n⏳ Next round coming up...")
            if use_tts and tts.backend != "none":
                import time
                time.sleep(2)
    
    return {
        "context": context,
        "rounds": rounds,
        "generated_at": datetime.now().isoformat(),
        "responses": all_responses,
        "tts_backend": tts.backend if use_tts and tts else "disabled"
    }


def main():
    parser = argparse.ArgumentParser(description="Run EPL debate with TTS")
    parser.add_argument("--context", "-c", help="Context JSON file")
    parser.add_argument("--rounds", "-r", type=int, default=2, help="Number of rounds")
    parser.add_argument("--no-tts", action="store_true", help="Disable TTS")
    parser.add_argument("--api-key", help="MiniMax API key (or set MINIMAX_API_KEY)")
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        print("⚠️  No MINIMAX_API_KEY set!")
        print("   Set with: export MINIMAX_API_KEY='your-key'")
        print("   Or pass --api-key\n")
    
    # Load context
    if args.context:
        context = load_context_from_file(args.context)
    else:
        # Default sample context
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
            ]
        }
    
    # Initialize
    client = MiniMaxClient(api_key if api_key else None)
    
    # Run debate
    result = run_debate_with_tts(
        client=client,
        context=context,
        rounds=args.rounds,
        use_tts=not args.no_tts
    )
    
    # Save
    filename = f"debate_tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Saved to {filename}")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    for r in result["responses"]:
        print(f"  [{r['persona_name']}] Round {r['round']}: {len(r.get('response', ''))} chars")


if __name__ == "__main__":
    main()
