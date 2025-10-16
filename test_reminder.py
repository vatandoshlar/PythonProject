#!/usr/bin/env python3
"""
Test script for reminder system
"""
import json
from datetime import datetime

def test_reminder_data():
    """Test the reminder system data structure"""
    print("🧪 Testing Reminder System Data")
    print("=" * 40)
    
    try:
        with open('registered_users.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Count users by status
        complete = [u for u in data if u.get('registration_status') == 'complete']
        incomplete = [u for u in data if u.get('registration_status') == 'incomplete']
        old_format = [u for u in data if 'registration_status' not in u]
        
        print(f"📊 Total users: {len(data)}")
        print(f"✅ Complete: {len(complete)}")
        print(f"⏳ Incomplete: {len(incomplete)}")
        print(f"🔄 Old format: {len(old_format)}")
        print()
        
        if incomplete:
            print("🔍 Incomplete users details:")
            for i, user in enumerate(incomplete, 1):
                print(f"{i}. User ID: {user.get('user_id', 'N/A')}")
                print(f"   Step: {user.get('current_step', 'N/A')}")
                print(f"   Last updated: {user.get('last_updated', 'N/A')}")
                print(f"   Username: @{user.get('username', 'N/A')}")
                print()
        else:
            print("❌ No incomplete users found")
            print("💡 To test, create incomplete users first")
        
        # Test step messages
        step_messages = {
            'fullname': "👤 Ismingizni kiriting",
            'country': "🌍 Davlatni tanlang", 
            'city': "🏙️ Shaharni kiriting",
            'birthdate': "📅 Tug'ilgan sanangizni kiriting",
            'phone': "📱 Telefon raqamingizni kiriting",
            'workplace': "🏢 Ish joyingizni kiriting",
            'specialty': "💼 Mutaxassisligingizni kiriting",
            'education': "🎓 Ma'lumot darajangizni tanlang",
            'nomination': "🏆 Nominatsiyani tanlang"
        }
        
        print("📝 Step messages:")
        for step, message in step_messages.items():
            print(f"   {step}: {message}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def create_test_incomplete_user():
    """Create a test incomplete user"""
    try:
        with open('registered_users.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if test user already exists
        if any(u.get('user_id') == 888888888 for u in data):
            print("ℹ️ Test user already exists")
            return
        
        test_user = {
            'user_id': 888888888,
            'username': 'test_reminder',
            'first_name': 'Test',
            'last_name': 'Reminder',
            'language_code': 'uz',
            'last_updated': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
            'registration_status': 'incomplete',
            'current_step': 'birthdate',
            'fullname': 'Test Reminder User',
            'country': 'Uzbekistan',
            'city': 'Tashkent'
        }
        
        data.append(test_user)
        
        with open('registered_users.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("✅ Test incomplete user created")
        print("User ID: 888888888")
        print("Step: birthdate")
        print("Status: incomplete")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")

if __name__ == "__main__":
    print("🚀 Reminder System Test")
    print("=" * 40)
    
    test_reminder_data()
    print()
    
    print("🔧 Creating test user...")
    create_test_incomplete_user()
    print()
    
    print("✅ Test completed!")
    print("\n📋 Next steps:")
    print("1. Start your bot: python3 bot.py")
    print("2. Send: /reminder")
    print("3. Check if reminders are sent")
