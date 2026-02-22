"""
Reset all transactional data for fresh testing.
Usage: python manage.py reset_data

Clears: Payment, Inspection, PartialReceiveItem, PartialReceive, OrderItem, PurchaseOrder
Resets: Project budgets (reserved_budget → 0)
Keeps: Users, Projects, ProjectParticipants (structure intact)
"""

from django.core.management.base import BaseCommand
from django.db import connection
from api.models import (
    Payment, Inspection, PartialReceiveItem, PartialReceive,
    OrderItem, PurchaseOrder, Project
)


class Command(BaseCommand):
    help = 'Reset all orders, receives, inspections, payments, and project budgets for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  This will DELETE all:\n'
                '   - Payments (การเบิกจ่าย)\n'
                '   - Inspections (ผลตรวจรับ)\n'
                '   - Partial Receives + Items (ใบรับของ)\n'
                '   - Order Items (รายการวัสดุ)\n'
                '   - Purchase Orders (ใบสั่งซื้อ)\n'
                '   - Reset Project budgets to 0\n'
                '\n   Users, Projects, and Participants will be KEPT.\n'
            ))
            confirm = input('Type "yes" to proceed: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Cancelled.'))
                return

        # Delete in dependency order
        counts = {}
        counts['payments'] = Payment.objects.all().delete()[0]
        counts['inspections'] = Inspection.objects.all().delete()[0]
        counts['partial_receive_items'] = PartialReceiveItem.objects.all().delete()[0]
        counts['partial_receives'] = PartialReceive.objects.all().delete()[0]
        counts['order_items'] = OrderItem.objects.all().delete()[0]
        counts['purchase_orders'] = PurchaseOrder.objects.all().delete()[0]

        # Reset project budgets
        updated = Project.objects.all().update(reserved_budget=0)
        # Trigger save to recalculate remaining_budget
        for project in Project.objects.all():
            project.save()

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Reset complete!\n'
            f'   Deleted: {counts["payments"]} payments, '
            f'{counts["inspections"]} inspections, '
            f'{counts["partial_receives"]} partial receives, '
            f'{counts["purchase_orders"]} purchase orders\n'
            f'   Reset budgets for {updated} projects\n'
        ))
