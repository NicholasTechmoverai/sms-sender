# temp_add_test_data.py
"""
Temporary script to add test data to the database for testing the user management UI.
Run this script to populate your database with sample users.

Usage:
    python temp_add_test_data.py
"""

import asyncio
import random
from datetime import datetime, timedelta
from tortoise import Tortoise, run_async
from tortoise.exceptions import DBConnectionError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = "asyncpg://ml_user:75223031@localhost:5432/zender"

# Sample data for generating realistic users
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Daniel", "Nancy", "Paul", "Lisa",
    "Mark", "Betty", "Donald", "Margaret", "George", "Sandra", "Kenneth", "Ashley",
    "Steven", "Kimberly", "Edward", "Emily", "Brian", "Donna", "Ronald", "Michelle"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
]

COUNTRIES = [
    "USA", "Canada", "UK", "Germany", "France", "Spain", "Italy", "Australia",
    "Japan", "Brazil", "India", "Mexico", "Netherlands", "Sweden", "Norway",
    "Denmark", "Switzerland", "Singapore", "UAE", "South Africa"
]

CITIES = {
    "USA": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Francisco", "Boston"],
    "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
    "UK": ["London", "Manchester", "Birmingham", "Liverpool", "Edinburgh"],
    "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne"],
    "France": ["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux"],
    "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Malaga"],
    "Italy": ["Rome", "Milan", "Naples", "Turin", "Florence"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
    "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Nagoya"],
    "Brazil": ["Sao Paulo", "Rio de Janeiro", "Brasilia", "Salvador", "Fortaleza"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
    "Mexico": ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana"],
    "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven"],
    "Sweden": ["Stockholm", "Gothenburg", "Malmo", "Uppsala", "Vasteras"],
    "Switzerland": ["Zurich", "Geneva", "Basel", "Bern", "Lausanne"],
    "Singapore": ["Singapore"],
    "UAE": ["Dubai", "Abu Dhabi", "Sharjah", "Al Ain"],
    "South Africa": ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth"]
}

DEPARTMENTS = [
    "engineering", "marketing", "sales", "human_resources", "finance",
    "research_development", "operations", "information_technology"
]

EXPERTISE_LEVELS = ["junior", "mid_level", "senior", "lead", "executive"]

SKILLS = {
    "engineering": ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript", "React", "Node.js", "Docker", "Kubernetes", "AWS", "SQL", "MongoDB", "GraphQL"],
    "marketing": ["SEO", "Content Marketing", "Social Media", "Email Marketing", "Analytics", "Brand Strategy", "PPC", "Copywriting"],
    "sales": ["Negotiation", "CRM", "Lead Generation", "Cold Calling", "Account Management", "Salesforce", "B2B Sales"],
    "human_resources": ["Recruitment", "Employee Relations", "Performance Management", "Training", "HRIS", "Labor Law"],
    "finance": ["Financial Analysis", "Budgeting", "Forecasting", "Excel", "QuickBooks", "Tax Planning", "Auditing"],
    "research_development": ["Research", "Data Analysis", "Lab Work", "Protocol Development", "Grant Writing", "Publication"],
    "operations": ["Project Management", "Supply Chain", "Logistics", "Process Improvement", "Six Sigma", "Inventory Management"],
    "information_technology": ["Network Security", "System Administration", "Cloud Computing", "IT Support", "Cybersecurity", "Database Administration"]
}

LANGUAGES = ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Korean", "Arabic", "Russian", "Portuguese", "Italian", "Dutch", "Swedish", "Danish", "Hindi"]

HOBBIES = [
    "Reading", "Hiking", "Photography", "Cooking", "Gaming", "Traveling", "Swimming", 
    "Cycling", "Yoga", "Painting", "Writing", "Gardening", "Running", "Fishing",
    "Chess", "Music", "Dancing", "Knitting", "Pottery", "Skiing", "Surfing"
]

PERSONALITY_TRAITS = [
    "Analytical", "Creative", "Detail-oriented", "Empathetic", "Energetic",
    "Patient", "Ambitious", "Curious", "Organized", "Adaptable", "Confident",
    "Diplomatic", "Innovative", "Reliable", "Sociable", "Thoughtful"
]

PHONE_PREFIXES = [
    "+1", "+44", "+49", "+33", "+34", "+39", "+61", "+81", "+55", "+91", "+52", "+31", "+46", "+41", "+65", "+971", "+27"
]

async def init_db():
    """Initialize database connection"""
    try:
        await Tortoise.init(
            db_url=DATABASE_URL,
            modules={"models": ["models"]}  # Adjust this path to your models
        )
        print("✅ Connected to database successfully")
    except DBConnectionError as e:
        print(f"❌ Failed to connect to database: {e}")
        print("Please check your database connection and try again.")
        raise

async def generate_phone_number(prefix):
    """Generate a random phone number"""
    number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    return f"{prefix}{number}"

async def create_test_users(count: int = 50):
    """Create test users in the database"""
    from models.index import Person, Department, ExpertiseLevel  # Import your models
    
    print(f"🚀 Creating {count} test users...")
    
    users_created = 0
    for i in range(count):
        try:
            # Generate basic info
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            name = f"{first_name} {last_name}"
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            
            # Location
            country = random.choice(COUNTRIES)
            city = random.choice(CITIES.get(country, ["Unknown"]))
            
            # Professional info
            department = random.choice(DEPARTMENTS)
            expertise_level = random.choice(EXPERTISE_LEVELS)
            years_experience = random.randint(0, 25)
            
            # Skills (3-7 random skills from relevant department)
            dept_skills = SKILLS.get(department, SKILLS["engineering"])
            num_skills = random.randint(3, 7)
            skills = random.sample(dept_skills, min(num_skills, len(dept_skills)))
            
            # Personal info
            age = random.randint(22, 65)
            birth_date = datetime.now() - timedelta(days=age*365)
            
            # Languages (1-4 languages)
            num_languages = random.randint(1, 4)
            languages = random.sample(LANGUAGES, num_languages)
            if "English" not in languages and random.random() > 0.3:
                languages.append("English")
            
            # Hobbies (2-5 hobbies)
            num_hobbies = random.randint(2, 5)
            hobbies = random.sample(HOBBIES, num_hobbies)
            
            # Personality traits (2-4 traits)
            num_traits = random.randint(2, 4)
            personality_traits = random.sample(PERSONALITY_TRAITS, num_traits)
            
            # Phone number (80% chance of having a phone)
            phone = None
            if random.random() < 0.8:
                prefix = random.choice(PHONE_PREFIXES)
                phone = await generate_phone_number(prefix)
            
            # Certifications (30% chance)
            certifications = []
            if random.random() < 0.3:
                cert_count = random.randint(1, 3)
                certifications = [f"Certification {j+1}" for j in range(cert_count)]
            
            # Create user
            user = await Person.create(
                form_number=f"FORM-{i+1:04d}-{random.randint(1000, 9999)}",
                name=name,
                email=email,
                age=age,
                birth_date=birth_date.date(),
                country=country,
                city=city,
                timezone=f"UTC{random.randint(-8, 8):+d}",
                remote_worker=random.choice([True, False]),
                department=department,
                expertise_level=expertise_level,
                years_experience=years_experience,
                skills=skills,
                certifications=certifications,
                languages=languages,
                hobbies=hobbies,
                personality_traits=personality_traits,
                favorite_color=random.choice(["Red", "Blue", "Green", "Yellow", "Purple", "Orange", "Black", "White"]),
                bio=f"Experienced {expertise_level} professional in {department}. Passionate about {random.choice(hobbies)} and {random.choice(skills)}.",
                phone=phone,
                profile_picture_url=f"https://randomuser.me/api/portraits/{random.choice(['men', 'women'])}/{random.randint(1, 99)}.jpg",
                is_active=True
            )
            
            users_created += 1
            if users_created % 10 == 0:
                print(f"  ✅ Created {users_created} users...")
                
        except Exception as e:
            print(f"  ❌ Failed to create user {i+1}: {e}")
    
    print(f"✅ Successfully created {users_created} test users!")

async def create_specific_test_scenarios():
    """Create specific test scenarios for UI testing"""
    from models.index import Person, Department, ExpertiseLevel
    
    print("🎯 Creating specific test scenarios...")
    
    # Scenario 1: Senior Python developers in Germany
    await Person.create(
        form_number="SPECIAL-001",
        name="Hans Schmidt",
        email="hans.schmidt@example.com",
        age=42,
        country="Germany",
        city="Berlin",
        department="engineering",
        expertise_level="senior",
        years_experience=15,
        skills=["Python", "Django", "AWS", "Docker", "Kubernetes"],
        languages=["German", "English"],
        phone="+4915123456789",
        is_active=True
    )
    
    await Person.create(
        form_number="SPECIAL-002",
        name="Klaus Weber",
        email="klaus.weber@example.com",
        age=38,
        country="Germany",
        city="Munich",
        department="engineering",
        expertise_level="senior",
        years_experience=12,
        skills=["Python", "FastAPI", "React", "TypeScript", "PostgreSQL"],
        languages=["German", "English", "French"],
        phone="+4915987654321",
        is_active=True
    )
    
    # Scenario 2: Marketing team in USA
    await Person.create(
        form_number="SPECIAL-003",
        name="Sarah Johnson",
        email="sarah.j@example.com",
        age=32,
        country="USA",
        city="New York",
        department="marketing",
        expertise_level="lead",
        years_experience=8,
        skills=["SEO", "Content Strategy", "Social Media", "Analytics", "Team Leadership"],
        languages=["English", "Spanish"],
        phone="+12125551234",
        is_active=True
    )
    
    # Scenario 3: Multi-lingual sales team
    await Person.create(
        form_number="SPECIAL-004",
        name="Maria Garcia",
        email="maria.g@example.com",
        age=29,
        country="Spain",
        city="Madrid",
        department="sales",
        expertise_level="mid_level",
        years_experience=5,
        skills=["B2B Sales", "CRM", "Negotiation", "Spanish Market"],
        languages=["Spanish", "English", "Catalan", "French"],
        phone="+34612345678",
        is_active=True
    )
    
    # Scenario 4: Remote worker with multiple skills
    await Person.create(
        form_number="SPECIAL-005",
        name="Alex Chen",
        email="alex.chen@example.com",
        age=35,
        country="Singapore",
        city="Singapore",
        department="information_technology",
        expertise_level="senior",
        years_experience=10,
        skills=["Cybersecurity", "Network Security", "Cloud Security", "Penetration Testing", "Risk Assessment"],
        certifications=["CISSP", "CEH", "AWS Security"],
        languages=["English", "Mandarin", "Cantonese"],
        phone="+6591234567",
        remote_worker=True,
        is_active=True
    )
    
    print("✅ Created specific test scenarios!")

async def verify_data():
    """Verify the data was inserted correctly"""
    from models.index import Person
    
    total_users = await Person.all().count()
    active_users = await Person.filter(is_active=True).count()
    
    # Get some stats
    dept_counts = {}
    for dept in DEPARTMENTS:
        count = await Person.filter(department=dept).count()
        if count > 0:
            dept_counts[dept] = count
    
    print("\n📊 Database Statistics:")
    print(f"  📊 Total users: {total_users}")
    print(f"  ✅ Active users: {active_users}")
    print("\n  📊 Users by department:")
    for dept, count in dept_counts.items():
        print(f"    • {dept}: {count}")
    
    # Sample some users
    sample_users = await Person.all().limit(5)
    print("\n👤 Sample users:")
    for user in sample_users:
        phone_status = "📱" if user.phone else "❌"
        print(f"  {phone_status} {user.name} - {user.department} - {user.country}/{user.city}")

async def clear_existing_data(confirm=True):
    """Clear existing data (use with caution)"""
    from models.index import Person
    
    if confirm:
        print("⚠️  This will delete ALL existing users!")
        response = input("Type 'YES' to confirm: ")
        if response != "YES":
            print("❌ Operation cancelled")
            return
    
    count = await Person.all().delete()
    print(f"🗑️  Deleted {count} existing users")

async def main():
    """Main function to run the script"""
    print("=" * 60)
    print("📦 TEST DATA GENERATOR FOR USER MANAGEMENT")
    print("=" * 60)
    
    try:
        # Initialize database
        await init_db()
        
        # Ask user what to do
        print("\n📋 Options:")
        print("  1. Add test data (keep existing)")
        print("  2. Clear all data and add fresh test data")
        print("  3. Just add specific test scenarios")
        print("  4. Just verify existing data")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "2":
            await clear_existing_data(confirm=True)
            await create_test_users(100)  # Create 100 test users
            await create_specific_test_scenarios()
        elif choice == "3":
            await create_specific_test_scenarios()
        elif choice == "4":
            await verify_data()
            return
        else:
            await create_test_users(50)  # Create 50 test users
            await create_specific_test_scenarios()
        
        # Verify the data
        await verify_data()
        
        print("\n✅ Test data generation complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close database connection
        await Tortoise.close_connections()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())