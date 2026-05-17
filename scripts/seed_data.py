import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole, Profile
from app.models.project import Project, ProjectStatus, Task
from app.models.invoice import Invoice, InvoiceStatus
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.blog import Blog, Testimonial, NewsletterSubscriber
from app.models.chat import ChatMessage
from datetime import datetime, timedelta, timezone

def seed_data():
    db = SessionLocal()

    try:
        print("Seeding database...")

        # Check if already seeded
        existing = db.query(User).filter(User.email == "admin@adrite.com").first()
        if existing:
            print("Database already seeded!")
            return

        # Create Admin
        admin = User(
            full_name="Admin User",
            email="admin@adrite.com",
            hashed_password=hash_password("Admin@1234"),
            role=UserRole.admin,
            is_active=True,
            is_verified=True
        )
        db.add(admin)
        db.flush()

        admin_profile = Profile(
            user_id=admin.id,
            bio="System Administrator",
            phone="+1234567890",
            company="Adrite Agency",
            country="USA"
        )
        db.add(admin_profile)

        # Create Client 1
        client1 = User(
            full_name="John Smith",
            email="john@example.com",
            hashed_password=hash_password("Client@1234"),
            role=UserRole.client,
            is_active=True,
            is_verified=True
        )
        db.add(client1)
        db.flush()

        client1_profile = Profile(
            user_id=client1.id,
            bio="Business Owner",
            phone="+1987654321",
            company="Smith Enterprises",
            country="UK"
        )
        db.add(client1_profile)

        # Create Client 2
        client2 = User(
            full_name="Sarah Johnson",
            email="sarah@example.com",
            hashed_password=hash_password("Client@1234"),
            role=UserRole.client,
            is_active=True,
            is_verified=True
        )
        db.add(client2)
        db.flush()

        client2_profile = Profile(
            user_id=client2.id,
            bio="Marketing Director",
            phone="+1122334455",
            company="Johnson Marketing",
            country="UAE"
        )
        db.add(client2_profile)

        # Create Projects
        project1 = Project(
            title="E-Commerce Website",
            description="Full stack e-commerce platform with payment integration",
            status=ProjectStatus.in_progress,
            budget=5000.00,
            deadline=datetime.now(timezone.utc) + timedelta(days=30),
            client_id=client1.id
        )
        db.add(project1)

        project2 = Project(
            title="Mobile App Development",
            description="iOS and Android app for food delivery service",
            status=ProjectStatus.pending,
            budget=8000.00,
            deadline=datetime.now(timezone.utc) + timedelta(days=60),
            client_id=client2.id
        )
        db.add(project2)

        project3 = Project(
            title="Brand Identity Design",
            description="Complete brand identity including logo and guidelines",
            status=ProjectStatus.completed,
            budget=2000.00,
            deadline=datetime.now(timezone.utc) - timedelta(days=5),
            client_id=client1.id
        )
        db.add(project3)
        db.flush()

        # Create Tasks
        task1 = Task(
            title="Setup project repository",
            description="Initialize GitHub repo and folder structure",
            status="completed",
            project_id=project1.id,
            assigned_to=admin.id
        )
        db.add(task1)

        task2 = Task(
            title="Design database schema",
            description="Create all required database tables",
            status="in_progress",
            project_id=project1.id,
            assigned_to=admin.id
        )
        db.add(task2)

        # Create Invoices
        invoice1 = Invoice(
            invoice_number="INV-001",
            amount=2500.00,
            status=InvoiceStatus.paid,
            due_date=datetime.now(timezone.utc) - timedelta(days=10),
            description="First milestone payment for E-Commerce Website",
            client_id=client1.id,
            project_id=project1.id
        )
        db.add(invoice1)

        invoice2 = Invoice(
            invoice_number="INV-002",
            amount=2500.00,
            status=InvoiceStatus.unpaid,
            due_date=datetime.now(timezone.utc) + timedelta(days=15),
            description="Second milestone payment for E-Commerce Website",
            client_id=client1.id,
            project_id=project1.id
        )
        db.add(invoice2)

        invoice3 = Invoice(
            invoice_number="INV-003",
            amount=4000.00,
            status=InvoiceStatus.unpaid,
            due_date=datetime.now(timezone.utc) + timedelta(days=30),
            description="First milestone payment for Mobile App",
            client_id=client2.id,
            project_id=project2.id
        )
        db.add(invoice3)

        # Create Tickets
        ticket1 = Ticket(
            subject="Login page not loading",
            description="The login page takes too long to load on mobile devices",
            status=TicketStatus.open,
            priority=TicketPriority.high,
            client_id=client1.id,
            project_id=project1.id
        )
        db.add(ticket1)

        ticket2 = Ticket(
            subject="Payment gateway issue",
            description="Stripe payment is failing for international cards",
            status=TicketStatus.in_progress,
            priority=TicketPriority.high,
            client_id=client1.id,
            project_id=project1.id
        )
        db.add(ticket2)

        ticket3 = Ticket(
            subject="Update company logo",
            description="Need to update the logo on all pages",
            status=TicketStatus.resolved,
            priority=TicketPriority.low,
            client_id=client2.id
        )
        db.add(ticket3)

        # Create Blogs
        blog1 = Blog(
            title="How We Build World Class Digital Products",
            content="At Adrite Agency we follow a rigorous process...",
            slug="how-we-build-world-class-digital-products",
            is_published=True,
            author_id=admin.id
        )
        db.add(blog1)

        blog2 = Blog(
            title="Top 10 Web Design Trends in 2026",
            content="Web design is constantly evolving...",
            slug="top-10-web-design-trends-2026",
            is_published=True,
            author_id=admin.id
        )
        db.add(blog2)

        blog3 = Blog(
            title="Why Your Business Needs a Mobile App",
            content="In todays digital world...",
            slug="why-your-business-needs-a-mobile-app",
            is_published=False,
            author_id=admin.id
        )
        db.add(blog3)

        # Create Testimonials
        testimonial1 = Testimonial(
            client_name="John Smith",
            company="Smith Enterprises",
            message="Adrite Agency delivered our project on time and exceeded expectations!",
            rating=5,
            is_published=True,
            client_id=client1.id
        )
        db.add(testimonial1)

        testimonial2 = Testimonial(
            client_name="Sarah Johnson",
            company="Johnson Marketing",
            message="Professional team with excellent communication throughout the project.",
            rating=5,
            is_published=True,
            client_id=client2.id
        )
        db.add(testimonial2)

        # Create Newsletter Subscribers
        sub1 = NewsletterSubscriber(email="subscriber1@example.com", is_active=True)
        sub2 = NewsletterSubscriber(email="subscriber2@example.com", is_active=True)
        db.add(sub1)
        db.add(sub2)

        # Create Chat Messages
        chat1 = ChatMessage(
            message="Hello, I need help with my project",
            response="Hi! I am here to help. What do you need?",
            client_id=client1.id
        )
        db.add(chat1)

        # Commit everything
        db.commit()
        print("Database seeded successfully!")
        print("\nTest Credentials:")
        print("Admin  → email: admin@adrite.com   | password: Admin@1234")
        print("Client → email: john@example.com   | password: Client@1234")
        print("Client → email: sarah@example.com  | password: Client@1234")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()