#!/usr/bin/env python3
"""
Random Joke Generator using external APIs.
Supports multiple joke sources with fallback options.
"""

import httpx
import json
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class Joke:
    """Joke data class"""
    text: str
    source: str
    category: Optional[str] = None
    type: str = "single"  # single or twopart
    setup: Optional[str] = None
    delivery: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def __str__(self) -> str:
        if self.type == "twopart":
            return f"{self.setup}\n{self.delivery}"
        return self.text
    
    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "source": self.source,
            "category": self.category,
            "type": self.type,
            "setup": self.setup,
            "delivery": self.delivery,
            "timestamp": self.timestamp
        }


class JokeGenerator:
    """Main Joke Generator class with multiple API sources"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.client = None
        self.jokes_cache = []
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    # ============ JokeAPI ============
    async def get_joke_from_jokeapi(self) -> Optional[Joke]:
        """
        Get joke from JokeAPI (jokeapi.dev)
        https://jokeapi.dev/
        """
        try:
            url = "https://v2.jokeapi.dev/joke/Any"
            response = await self.client.get(url)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if data.get("error"):
                return None
            
            if data.get("type") == "twopart":
                joke = Joke(
                    text=f"{data['setup']}\n{data['delivery']}",
                    source="JokeAPI",
                    category=data.get("category"),
                    type="twopart",
                    setup=data.get("setup"),
                    delivery=data.get("delivery")
                )
            else:
                joke = Joke(
                    text=data.get("joke", ""),
                    source="JokeAPI",
                    category=data.get("category"),
                    type="single"
                )
            
            return joke
        except Exception as e:
            print(f"❌ JokeAPI error: {e}")
            return None
    
    # ============ Official Joke API ============
    async def get_joke_from_official_api(self) -> Optional[Joke]:
        """
        Get joke from Official Joke API (official-joke-api.appspot.com)
        https://github.com/15Dkatz/official_joke_api
        """
        try:
            url = "https://official-joke-api.appspot.com/jokes/random"
            response = await self.client.get(url)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            joke = Joke(
                text=f"{data['setup']}\n{data['punchline']}",
                source="Official Joke API",
                category=data.get("type"),
                type="twopart",
                setup=data.get("setup"),
                delivery=data.get("punchline")
            )
            
            return joke
        except Exception as e:
            print(f"❌ Official Joke API error: {e}")
            return None
    
    # ============ UselessFacts (Fun Facts) ============
    async def get_fun_fact(self) -> Optional[Joke]:
        """
        Get fun fact from UselessFacts API
        https://uselessfacts.jsondump.com/
        """
        try:
            url = "https://uselessfacts.jsondump.com/random.json"
            response = await self.client.get(url)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            joke = Joke(
                text=data.get("text", ""),
                source="Useless Facts API",
                type="single"
            )
            
            return joke
        except Exception as e:
            print(f"❌ Useless Facts API error: {e}")
            return None
    
    # ============ Quote API ============
    async def get_funny_quote(self) -> Optional[Joke]:
        """
        Get random quote from Quotable API
        https://quotable.io/
        """
        try:
            url = "https://api.quotable.io/random"
            response = await self.client.get(url)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            joke = Joke(
                text=f"{data['content']}\n— {data['author']}",
                source="Quotable API",
                category=", ".join(data.get("tags", [])),
                type="single"
            )
            
            return joke
        except Exception as e:
            print(f"❌ Quotable API error: {e}")
            return None
    
    # ============ Chuck Norris Jokes ============
    async def get_chuck_norris_joke(self) -> Optional[Joke]:
        """
        Get Chuck Norris joke from API (api.chucknorris.io)
        https://api.chucknorris.io/
        """
        try:
            url = "https://api.chucknorris.io/jokes/random"
            response = await self.client.get(url)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            joke = Joke(
                text=data.get("value", ""),
                source="Chuck Norris API",
                category=data.get("category"),
                type="single"
            )
            
            return joke
        except Exception as e:
            print(f"❌ Chuck Norris API error: {e}")
            return None
    
    # ============ Dad Jokes ============
    async def get_dad_joke(self) -> Optional[Joke]:
        """
        Get dad joke from icanhazdadjoke.com
        https://icanhazdadjoke.com/
        """
        try:
            url = "https://icanhazdadjoke.com/"
            response = await self.client.get(
                url,
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            joke = Joke(
                text=data.get("joke", ""),
                source="icanhazdadjoke",
                type="single"
            )
            
            return joke
        except Exception as e:
            print(f"❌ Dad Jokes API error: {e}")
            return None
    
    # ============ Main Generator Methods ============
    async def get_random_joke(self) -> Optional[Joke]:
        """Get a random joke from any available source"""
        sources = [
            self.get_joke_from_jokeapi,
            self.get_joke_from_official_api,
            self.get_chuck_norris_joke,
            self.get_dad_joke,
        ]
        
        random.shuffle(sources)
        
        for source in sources:
            joke = await source()
            if joke:
                return joke
        
        return None
    
    async def get_jokes_by_category(self, category: str = "Any", count: int = 5) -> List[Joke]:
        """Get multiple jokes from JokeAPI by category"""
        jokes = []
        
        for i in range(count):
            try:
                url = f"https://v2.jokeapi.dev/joke/{category}"
                response = await self.client.get(url)
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                
                if data.get("error"):
                    continue
                
                if data.get("type") == "twopart":
                    joke = Joke(
                        text=f"{data['setup']}\n{data['delivery']}",
                        source="JokeAPI",
                        category=data.get("category"),
                        type="twopart",
                        setup=data.get("setup"),
                        delivery=data.get("delivery")
                    )
                else:
                    joke = Joke(
                        text=data.get("joke", ""),
                        source="JokeAPI",
                        category=data.get("category"),
                        type="single"
                    )
                
                jokes.append(joke)
            except Exception as e:
                print(f"❌ Error fetching joke {i+1}: {e}")
                continue
        
        return jokes
    
    async def get_all_sources(self) -> Dict[str, Optional[Joke]]:
        """Get one joke from each available source"""
        results = {}
        
        results["JokeAPI"] = await self.get_joke_from_jokeapi()
        results["Official Joke API"] = await self.get_joke_from_official_api()
        results["Fun Facts"] = await self.get_fun_fact()
        results["Random Quote"] = await self.get_funny_quote()
        results["Chuck Norris"] = await self.get_chuck_norris_joke()
        results["Dad Jokes"] = await self.get_dad_joke()
        
        return results
    
    def cache_joke(self, joke: Joke) -> None:
        """Cache a joke"""
        self.jokes_cache.append(joke)
    
    def get_cached_jokes(self) -> List[Joke]:
        """Get all cached jokes"""
        return self.jokes_cache
    
    def clear_cache(self) -> None:
        """Clear joke cache"""
        self.jokes_cache = []


# ============ Utility Functions ============
async def print_joke(joke: Optional[Joke]) -> None:
    """Print a joke with formatting"""
    if not joke:
        print("❌ Failed to fetch joke")
        return
    
    print("\n" + "="*70)
    print(f"📝 {joke.source}")
    if joke.category:
        print(f"📂 Category: {joke.category}")
    print("="*70)
    print(f"\n{joke.text}\n")
    print("="*70 + "\n")


async def main():
    """Example usage"""
    async with JokeGenerator() as generator:
        
        # 1. Get a random joke
        print("🎲 Random Joke:")
        joke = await generator.get_random_joke()
        await print_joke(joke)
        
        # 2. Get jokes by category
        print("\n📚 5 Programming Jokes:")
        jokes = await generator.get_jokes_by_category("Programming", count=3)
        for i, j in enumerate(jokes, 1):
            print(f"\n{i}. {j.text}\n")
        
        # 3. Get from all sources
        print("\n🌍 All Sources:")
        all_jokes = await generator.get_all_sources()
        for source, joke in all_jokes.items():
            if joke:
                print(f"\n✓ {source}:")
                print(f"  {joke.text[:80]}...")
            else:
                print(f"\n✗ {source}: Failed")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
