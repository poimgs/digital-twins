#!/usr/bin/env python3
"""
Script to add additional seed data for development and testing
"""

import asyncio
import asyncpg
import json
from datetime import datetime

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/digital_twin_bot"

async def add_seed_data():
    """Add additional seed data for testing"""
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Add more diverse stories
        additional_stories = [
            {
                'story_id': 'alice_story_003',
                'twin_id': 'alice_chen',
                'title': 'Learning React the Hard Way',
                'full_content': 'When React first came out, I was skeptical. I had been using jQuery for years and thought, "Why do I need this complicated framework?" But my team decided to rebuild our main product in React, and I was assigned to the project. The first few weeks were brutal. I kept thinking in jQuery terms, manipulating the DOM directly and fighting against React\'s paradigms. I remember spending an entire weekend trying to figure out why my component wasn\'t re-rendering, only to discover I was mutating state directly. The breakthrough came when I finally understood the concept of "thinking in React" - building components as pure functions of their props and state. Now I can\'t imagine building complex UIs without it.',
                'themes': ['technology', 'learning', 'adaptation', 'growth'],
                'emotional_tone': 'reflective',
                'adaptability_level': 0.7,
                'key_facts': ['skeptical at first', 'spent weekend debugging', 'breakthrough with pure functions', 'now loves React'],
                'conversation_triggers': ['React', 'JavaScript', 'frontend', 'learning new technology', 'paradigm shift']
            },
            {
                'story_id': 'bob_story_003',
                'twin_id': 'bob_martinez',
                'title': 'The Storm That Made Everything Clear',
                'full_content': 'I was photographing the Northern Lights in Iceland when this massive storm rolled in. The forecast said it would pass quickly, but instead it got worse. Winds were howling at 80 mph, and I could barely keep my camera steady. Most photographers would have packed up and gone inside, but something told me to stay. Through the storm clouds, the aurora started dancing in ways I\'d never seen before - these incredible green and purple curtains that seemed to be fighting with the wind. The combination of the storm and the lights created this otherworldly scene. I was completely soaked and freezing, but I kept shooting. One of those photos became the most popular image on my Instagram, and it taught me that sometimes the best shots come from the worst conditions.',
                'themes': ['photography', 'perseverance', 'nature', 'intuition'],
                'emotional_tone': 'exhilarating',
                'adaptability_level': 0.9,
                'key_facts': ['Iceland Northern Lights', '80 mph winds', 'stayed during storm', 'most popular Instagram photo'],
                'conversation_triggers': ['Northern Lights', 'Iceland', 'storm', 'photography', 'perseverance', 'Instagram']
            },
            {
                'story_id': 'sarah_story_003',
                'twin_id': 'sarah_kim',
                'title': 'The Day I Stopped Being a Therapist',
                'full_content': 'It was a Tuesday afternoon when I realized I needed to stop practicing therapy. I was sitting across from a client who was describing their trauma, and instead of feeling empathy, I felt... nothing. Complete emotional numbness. I had been working with difficult cases for eight years, and I had hit a wall. That night, I went home and couldn\'t stop crying. I realized I had been carrying everyone else\'s pain for so long that I had forgotten how to feel my own emotions. It took me six months to make the decision to transition away from therapy and toward writing. The hardest part was feeling like I was abandoning people who needed help. But I realized that staying in a profession where I was emotionally depleted wouldn\'t help anyone. Writing became my way of processing all those years of human stories, and it allowed me to help people in a different way.',
                'themes': ['career transition', 'burnout', 'self-care', 'emotional health'],
                'emotional_tone': 'vulnerable',
                'adaptability_level': 0.6,
                'key_facts': ['felt emotional numbness', 'eight years of practice', 'six months to decide', 'transition to writing'],
                'conversation_triggers': ['burnout', 'career change', 'therapy', 'emotional exhaustion', 'self-care']
            }
        ]
        
        # Insert additional stories
        for story in additional_stories:
            await conn.execute("""
                INSERT INTO stories (story_id, twin_id, title, full_content, themes, emotional_tone, adaptability_level, key_facts, conversation_triggers)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (story_id) DO NOTHING
            """, 
            story['story_id'], story['twin_id'], story['title'], story['full_content'],
            story['themes'], story['emotional_tone'], story['adaptability_level'],
            json.dumps(story['key_facts']), story['conversation_triggers']
            )
        
        # Add more test users with different profiles
        test_users = [
            {
                'chat_id': 987654321,
                'profile': {
                    "name": "Alex Developer",
                    "interests": ["programming", "AI", "coffee"],
                    "occupation": "Software Developer",
                    "location": "Seattle"
                }
            },
            {
                'chat_id': 555666777,
                'profile': {
                    "name": "Maria Photographer", 
                    "interests": ["travel", "photography", "art"],
                    "occupation": "Freelance Photographer",
                    "location": "Barcelona"
                }
            }
        ]
        
        for user in test_users:
            await conn.execute("""
                INSERT INTO user_memory (chat_id, profile) 
                VALUES ($1, $2) 
                ON CONFLICT (chat_id) DO NOTHING
            """, user['chat_id'], json.dumps(user['profile']))
        
        print("✅ Additional seed data added successfully!")
        print(f"   - Added {len(additional_stories)} more stories")
        print(f"   - Added {len(test_users)} test users")
        
    except Exception as e:
        print(f"❌ Error adding seed data: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(add_seed_data())