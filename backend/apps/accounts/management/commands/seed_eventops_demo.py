from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Role, UserProfile
from apps.clients.models import Client, ClientContact
from apps.common.constants import (
    ALL_ROLES,
    ROLE_ACCOUNTANT,
    ROLE_ADMIN,
    ROLE_CASHIER,
    ROLE_DRIVER,
    ROLE_OPERATIONS,
    ROLE_OWNER,
    ROLE_SALES,
    ROLE_TECHNICIAN,
    ROLE_VIEWER,
)
from apps.drivers.models import Driver, DriverPayment, DriverTrip
from apps.finance.models import (
    BankAccount,
    CashTransaction,
    Cashbox,
    Expense,
    ExpenseCategory,
    Invoice,
    InvoiceItem,
    Payment,
    PaymentMethod,
)
from apps.inventory.models import InventoryTransaction, Item, ItemCategory, ItemReservation
from apps.notifications.models import Notification
from apps.orders.models import (
    JobDriverAssignment,
    JobSchedule,
    JobStaffAssignment,
    JobTask,
    JobVendorAssignment,
    Order,
    OrderItem,
    OrderStatusHistory,
)
from apps.payroll.models import PayrollLine, PayrollPeriod
from apps.quotations.models import Quotation, QuotationItem
from apps.staff.models import StaffAdvance, StaffBonus, StaffDeduction, StaffProfile
from apps.vendors.models import Vendor, VendorPayment, VendorTransaction


ROLE_META = {
    ROLE_OWNER: ("General Manager", "المدير العام", True, True, True),
    ROLE_ADMIN: ("System Administrator", "مدير النظام", False, False, True),
    ROLE_SALES: ("Sales Officer", "موظف المبيعات", False, False, False),
    ROLE_OPERATIONS: ("Operations Manager", "مدير التشغيل", False, False, False),
    ROLE_ACCOUNTANT: ("Accountant", "المحاسب", True, True, False),
    ROLE_TECHNICIAN: ("Technician", "الفني", False, False, False),
    ROLE_DRIVER: ("Driver", "السائق", False, False, False),
    ROLE_CASHIER: ("Cashier", "أمين الخزنة", False, False, False),
    ROLE_VIEWER: ("System Observer", "مراقب النظام", False, False, False),
}

DEMO_USERS = {
    ROLE_OWNER: "owner@example.com",
    ROLE_ADMIN: "admin@example.com",
    ROLE_SALES: "sales@example.com",
    ROLE_OPERATIONS: "operations@example.com",
    ROLE_ACCOUNTANT: "accountant@example.com",
    ROLE_TECHNICIAN: "technician@example.com",
    ROLE_DRIVER: "driver@example.com",
    ROLE_CASHIER: "cashier@example.com",
    ROLE_VIEWER: "viewer@example.com",
}

LEGACY_DEMO_USERNAMES = {
    ROLE_OWNER: "owner",
    ROLE_ADMIN: "admin",
    ROLE_SALES: "sales",
    ROLE_OPERATIONS: "operations",
    ROLE_ACCOUNTANT: "accountant",
    ROLE_TECHNICIAN: "technician",
    ROLE_DRIVER: "driver",
    ROLE_CASHIER: "cashier",
    ROLE_VIEWER: "viewer",
}


class Command(BaseCommand):
    help = "Seed realistic Arabic EventOps demo data for an Egyptian operations company."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Reset demo data first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            call_command("reset_demo_data")

        users = self.seed_users()
        categories, items = self.seed_inventory(users)
        clients = self.seed_clients()
        vendors = self.seed_vendors()
        drivers = self.seed_drivers(users)
        staff = self.seed_staff(users)
        methods, cashboxes, bank = self.seed_finance_lookups()
        orders = self.seed_orders(users, clients, items, vendors, drivers, staff)
        self.seed_quotations(users, clients, items)
        invoices = self.seed_invoices(users, orders)
        self.seed_payments(users, orders, invoices, methods, cashboxes, bank)
        self.seed_expenses(users, orders, vendors, cashboxes)
        self.seed_vendor_driver_settlements(users, orders, vendors, drivers)
        self.seed_cashbox_movements(users, cashboxes, orders)
        self.seed_payroll(users, staff)
        self.seed_notifications(users)

        self.stdout.write(self.style.SUCCESS("Arabic EventOps demo data seeded."))
        self.stdout.write("Demo login emails use password: Admin12345")

    def seed_users(self):
        User = get_user_model()
        users = {}
        for code in ALL_ROLES:
            name_en, name_ar, can_profit, can_payroll, can_approve = ROLE_META[code]
            role, _ = Role.objects.update_or_create(
                code=code,
                defaults={
                    "name_en": name_en,
                    "name_ar": name_ar,
                    "can_view_profit": can_profit,
                    "can_view_payroll": can_payroll,
                    "can_approve": can_approve,
                },
            )
            email = DEMO_USERS[code]
            user, _ = User.objects.update_or_create(
                username=email,
                defaults={
                    "email": email,
                    "first_name": name_ar,
                    "last_name": "",
                    "role": role,
                    "language": "ar",
                    "theme": "light",
                    "is_staff": code in [ROLE_OWNER, ROLE_ADMIN],
                    "is_superuser": code == ROLE_OWNER,
                    "is_active": True,
                },
            )
            user.set_password("Admin12345")
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "job_title": name_ar,
                    "preferred_language": "ar",
                    "preferred_theme": "light",
                },
            )
            legacy_username = LEGACY_DEMO_USERNAMES.get(code)
            if legacy_username:
                User.objects.filter(username=legacy_username).update(
                    first_name=name_ar,
                    last_name="",
                    role=role,
                    language="ar",
                    theme="light",
                    is_active=True,
                )
                legacy_user = User.objects.filter(username=legacy_username).first()
                if legacy_user:
                    legacy_user.set_password("Admin12345")
                    legacy_user.save()
                    UserProfile.objects.update_or_create(
                        user=legacy_user,
                        defaults={
                            "job_title": name_ar,
                            "preferred_language": "ar",
                            "preferred_theme": "light",
                        },
                    )
            users[code] = user
        return users

    def seed_inventory(self, users):
        category_names = [
            "شاشات LED",
            "أنظمة صوتية",
            "إضاءة",
            "أعمال خشبية",
            "طاولات وأثاث",
            "معدات إعلامية",
            "مولدات كهربائية",
            "خدمات نقل",
            "خدمات فنيين",
            "خدمات موردين خارجيين",
        ]
        categories = {
            name: ItemCategory.objects.create(name=name, notes=f"تصنيف تشغيلي: {name}")
            for name in category_names
        }
        item_rows = [
            ("LED-P3-IN", "شاشة LED داخلية P3", "شاشات LED", "كابينة", 160, 122, 30, 4, 4, 650, 280, "كابينة شاشة داخلية مناسبة للمؤتمرات وقاعات الفنادق."),
            ("LED-P4-OUT", "شاشة LED خارجية P4", "شاشات LED", "متر مربع", 90, 72, 12, 3, 3, 900, 420, "شاشة خارجية عالية السطوع للفعاليات المفتوحة."),
            ("DSP-55", "شاشة عرض 55 بوصة", "شاشات LED", "قطعة", 18, 14, 2, 1, 1, 1800, 700, "شاشة عرض احترافية للبوثات وقاعات التدريب."),
            ("SND-MIX12", "ميكسر صوت 12 قناة", "أنظمة صوتية", "قطعة", 8, 6, 1, 0, 1, 1500, 500, "ميكسر صوت مناسب للمؤتمرات المتوسطة."),
            ("MIC-WL-SET", "طقم ميكروفون لاسلكي", "أنظمة صوتية", "طقم", 24, 19, 4, 1, 0, 450, 120, "طقم ميكروفونات لاسلكية للاجتماعات والعروض."),
            ("SPK-1000W", "سماعة 1000 وات", "أنظمة صوتية", "قطعة", 32, 24, 6, 1, 1, 700, 220, "سماعة خارجية قوية مع ستاند تشغيل."),
            ("LGT-PAR", "إضاءة مسرح PAR", "إضاءة", "قطعة", 48, 36, 8, 2, 2, 180, 65, "وحدة إضاءة ملونة للمسرح والبوثات."),
            ("LGT-MH", "إضاءة متحركة Moving Head", "إضاءة", "قطعة", 24, 17, 5, 1, 1, 450, 160, "إضاءة متحركة للعروض والافتتاحات."),
            ("WOOD-BOOTH-M", "متر بوث خشبي", "أعمال خشبية", "متر", 120, 90, 20, 4, 6, 750, 360, "تنفيذ بوث خشبي شامل التشطيب الأساسي."),
            ("TBL-EVENT", "طاولة فعاليات", "طاولات وأثاث", "قطعة", 60, 46, 10, 2, 2, 180, 60, "طاولة قابلة للطي للمعارض وورش العمل."),
            ("GEN-30KVA", "مولد كهرباء 30 كيلو", "مولدات كهربائية", "قطعة", 5, 3, 1, 0, 1, 3500, 1700, "مولد ديزل احتياطي للفعاليات الخارجية."),
            ("CBL-HDMI", "كابل HDMI", "معدات إعلامية", "قطعة", 80, 64, 10, 3, 3, 80, 25, "كابل HDMI بطول مناسب لتوصيلات العرض."),
            ("PLY-MEDIA", "مشغل وسائط", "معدات إعلامية", "قطعة", 16, 12, 2, 1, 1, 650, 180, "مشغل وسائط لتشغيل المحتوى على الشاشات."),
            ("TRS-STAND", "ستاند تراس", "إضاءة", "قطعة", 40, 30, 8, 1, 1, 220, 80, "ستاند تراس لتركيب الإضاءة والشاشات الصغيرة."),
        ]
        items = {}
        for sku, name, category, unit, total, available, reserved, damaged, maintenance, price, cost, description in item_rows:
            item = Item.objects.create(
                sku=sku,
                name=name,
                notes=description,
                category=categories[category],
                unit=unit,
                total_quantity=total,
                available_quantity=available,
                reserved_quantity=reserved,
                damaged_quantity=damaged,
                maintenance_quantity=maintenance,
                rental_price=Decimal(price),
                replacement_cost=Decimal(cost),
                location="المخزن الرئيسي - مدينة نصر",
                is_active=True,
            )
            InventoryTransaction.objects.create(
                item=item,
                transaction_type="adjustment",
                quantity=max(total, 1),
                reference="رصيد افتتاحي",
                notes="رصيد افتتاحي من ملف متابعة المخزون والتوفر.",
                created_by=users[ROLE_OPERATIONS],
            )
            items[sku] = item
        return categories, items

    def seed_clients(self):
        rows = [
            ("شركة النيل للفعاليات", "01001112220", "events@nileagency.eg", "مدينة نصر، القاهرة", "منى حسن", "agency", 120000, "سداد خلال 7 أيام", "عميل متكرر لفعاليات الشركات والمؤتمرات."),
            ("دلتا فارما", "01002223330", "events@deltapharma.eg", "التجمع الخامس، القاهرة الجديدة", "د. هاني فؤاد", "company", 250000, "سداد خلال 14 يوم", "شركة أدوية تحتاج مؤتمرات علمية وتجهيزات عرض."),
            ("قاعة رويال للمؤتمرات", "01003334440", "booking@royalhall.eg", "مصر الجديدة، القاهرة", "نور مجدي", "company", 160000, "دفعة مقدمة 50%", "قاعة مؤتمرات تعتمد على تجهيزات شاشة وصوت."),
            ("أكاديمية المستقبل", "01006667770", "events@futureacademy.edu.eg", "المعادي، القاهرة", "أحمد ناصر", "company", 110000, "سداد خلال 7 أيام", "فعاليات تعليمية وحفلات تخرج سنوية."),
            ("وكالة سمارت إكسبو", "01004445550", "ops@smartexpo.eg", "الحي المتميز، 6 أكتوبر", "كريم سعد", "agency", 180000, "سداد خلال 10 أيام", "وكالة معارض تحتاج بوثات وشاشات."),
            ("شركة القناة للدعاية", "01008889990", "accounts@canalmarketing.eg", "الإسماعيلية", "عمر سالم", "agency", 150000, "سداد خلال 10 أيام", "حملات تسويقية خارجية وفعاليات ميدانية."),
            ("قاعة النور للاحتفالات", "01007778880", "booking@alnoorhall.eg", "المنصورة", "مي طارق", "company", 85000, "نقدي أو دفعات", "قاعة أفراح ومناسبات تحتاج أنظمة صوت وإضاءة."),
            ("فندق رويال الإسماعيلية", "01005556660", "banquet@royalismailia.eg", "كورنيش الإسماعيلية", "سارة عادل", "company", 200000, "سداد خلال 15 يوم", "فندق يستضيف مؤتمرات وحفلات كبرى."),
            ("شركة الأهرام للتسويق", "01009990011", "marketing@ahramagency.eg", "الدقي، الجيزة", "محمود كامل", "agency", 130000, "دفعة مقدمة 40%", "تنشيطات تسويقية ومعارض متنقلة."),
            ("جامعة المستقبل الخاصة", "01006668899", "events@futureuniv.edu.eg", "القاهرة الجديدة", "دينا مراد", "company", 220000, "سداد خلال 21 يوم", "حفلات تخرج ومؤتمرات طلابية."),
        ]
        clients = {}
        for name, phone, email, address, contact, client_type, limit, terms, notes in rows:
            client = Client.objects.create(
                name=name,
                client_type=client_type,
                phone=phone,
                email=email,
                address=address,
                credit_limit=Decimal(limit),
                notes=f"{notes} شروط السداد: {terms}. واتساب: {phone}.",
            )
            ClientContact.objects.create(
                client=client,
                name=contact,
                position="منسق فعاليات",
                phone=phone,
                email=email,
                is_primary=True,
            )
            clients[name] = client
        return clients

    def seed_vendors(self):
        rows = [
            ("برايت لتأجير الشاشات", "تأجير شاشات LED", "01010001001", "مدينة نصر، القاهرة"),
            ("برو ساوند مصر", "أنظمة صوتية", "01010001002", "مصر الجديدة، القاهرة"),
            ("القاهرة للأعمال الخشبية", "تنفيذ بوثات خشبية", "01010001003", "شبرا، القاهرة"),
            ("نقل الفعاليات السريع", "نقل وتجهيزات", "01010001004", "العبور، القليوبية"),
            ("باور جين للمولدات", "تأجير مولدات", "01010001005", "العاشر من رمضان"),
            ("ميديا هاوس برودكشن", "تصوير ومحتوى إعلامي", "01010001006", "الدقي، الجيزة"),
        ]
        return {
            name: Vendor.objects.create(
                name=name,
                service_type=kind,
                phone=phone,
                address=address,
                payment_terms="50% مقدم والباقي بعد انتهاء الفعالية",
                notes="مورد معتمد في قاعدة بيانات التشغيل.",
            )
            for name, kind, phone, address in rows
        }

    def seed_drivers(self, users):
        rows = [
            ("أحمد حسن", "01022220101", "نقل ثقيل", "ط س م 2457", 1200),
            ("محمد سمير", "01022220102", "بيك أب", "س و ر 8193", 850),
            ("كريم عادل", "01022220103", "فان مغلق", "م ر أ 6631", 700),
            ("مصطفى فتحي", "01022220104", "نقل ثقيل", "ق ل ب 9344", 1300),
            ("إسلام نبيل", "01022220105", "ربع نقل", "ن هـ د 5812", 900),
        ]
        drivers = {}
        for index, (name, phone, vehicle, plate, cost) in enumerate(rows):
            driver = Driver.objects.create(
                name=name,
                user=users[ROLE_DRIVER] if index == 0 else None,
                phone=phone,
                vehicle_type=vehicle,
                vehicle_plate=plate,
                license_number=f"DRV-2026-{index + 1:03d}",
                day_rate=Decimal(cost),
                notes="سائق معتمد لرحلات نقل معدات الفعاليات.",
            )
            drivers[name] = driver
        return drivers

    def seed_staff(self, users):
        rows = [
            ("عمر علي", "مدير تشغيل", 18000, 1200, users[ROLE_OPERATIONS]),
            ("محمود رضا", "فني أول", 10000, 850, None),
            ("يوسف نبيل", "فني شاشات", 8500, 700, users[ROLE_TECHNICIAN]),
            ("إسلام فاروق", "فني صوتيات", 8000, 650, None),
            ("سارة أحمد", "محاسبة", 12000, 0, users[ROLE_ACCOUNTANT]),
            ("دينا مصطفى", "مبيعات", 9000, 0, users[ROLE_SALES]),
            ("حسن إبراهيم", "أمين خزنة", 7500, 0, users[ROLE_CASHIER]),
        ]
        staff = {}
        for name, role, salary, rate, user in rows:
            staff[name] = StaffProfile.objects.create(
                name=name,
                user=user,
                phone="0103333" + str(len(staff) + 101).zfill(4),
                staff_role=role,
                hire_date=timezone.localdate() - timedelta(days=420),
                base_salary=Decimal(salary),
                day_rate=Decimal(rate),
                notes="بيانات موظف ضمن فريق التشغيل التجريبي.",
            )
        return staff

    def seed_finance_lookups(self):
        methods = {
            name: PaymentMethod.objects.create(name=name, method_type=kind)
            for name, kind in [
                ("نقدي", "cash"),
                ("تحويل بنكي", "bank"),
                ("إنستاباي", "digital"),
                ("فودافون كاش", "digital"),
                ("شيك", "cheque"),
            ]
        }
        cashboxes = {
            "الخزنة الرئيسية": Cashbox.objects.create(name="الخزنة الرئيسية", opening_balance=Decimal("25000"), currency="EGP", notes="خزنة التحصيل الرئيسية."),
            "عهدة التشغيل": Cashbox.objects.create(name="عهدة التشغيل", opening_balance=Decimal("8000"), currency="EGP", notes="عهدة يومية لمصاريف التشغيل."),
        }
        bank = BankAccount.objects.create(
            name="حساب الشركة الرئيسي",
            bank_name="CIB",
            account_number="EG2600012345",
            opening_balance=Decimal("120000"),
        )
        return methods, cashboxes, bank

    def aware(self, days, hour):
        day = timezone.localdate() + timedelta(days=days)
        return timezone.make_aware(datetime.combine(day, datetime.min.time())).replace(hour=hour)

    def seed_orders(self, users, clients, items, vendors, drivers, staff):
        specs = [
            ("ORD-2026-05-0001", "مؤتمر شركة أدوية", "دلتا فارما", "فندق رويال الإسماعيلية - القاعة الكبرى", "completed", -7, 148000),
            ("ORD-2026-05-0002", "حفل زفاف بفندق رويال", "فندق رويال الإسماعيلية", "حديقة فندق رويال الإسماعيلية", "fully_paid", -5, 78000),
            ("ORD-2026-05-0003", "حفل تخرج جامعة المستقبل", "جامعة المستقبل الخاصة", "ساحة جامعة المستقبل الرئيسية", "event_running", 0, 132000),
            ("ORD-2026-05-0004", "الاجتماع السنوي لشركة النيل", "شركة النيل للفعاليات", "فندق تريومف - القاهرة", "scheduled", 4, 96000),
            ("ORD-2026-05-0005", "إطلاق منتج جديد", "شركة القناة للدعاية", "قصر ثقافة الإسماعيلية", "confirmed", 8, 118000),
            ("ORD-2026-05-0006", "تجهيز جناح معرض", "وكالة سمارت إكسبو", "مركز مصر للمعارض الدولية", "in_progress", 1, 164000),
            ("ORD-2026-05-0007", "تأجير نظام صوت خارجي", "قاعة النور للاحتفالات", "استاد المنصورة", "installed", 3, 72000),
            ("ORD-2026-05-0008", "فعالية تسويقية خارجية", "شركة الأهرام للتسويق", "مول مصر - ساحة خارجية", "waiting_client_confirmation", 12, 54000),
            ("ORD-2026-05-0009", "تجهيز قاعة تدريب", "دلتا فارما", "مقر دلتا فارما - القاهرة الجديدة", "partially_paid", -3, 42000),
            ("ORD-2026-05-0010", "تجهيز منصة مؤتمر حكومي", "شركة النيل للفعاليات", "العاصمة الإدارية الجديدة", "waiting_availability", 14, 210000),
            ("ORD-2026-05-0011", "خلفية LED لمؤتمر صحفي", "وكالة سمارت إكسبو", "فندق ماريوت القاهرة", "dismantling", -1, 87000),
            ("ORD-2026-05-0012", "حفل عشاء فندقي", "قاعة رويال للمؤتمرات", "قاعة رويال للمؤتمرات - مصر الجديدة", "new_inquiry", 16, 68000),
            ("ORD-2026-05-0013", "بوث طبي خشبي", "دلتا فارما", "إنتركونتيننتال سيتي ستارز", "draft_quotation", 18, 74000),
            ("ORD-2026-05-0014", "شاشة صغيرة لتنشيط مول", "شركة الأهرام للتسويق", "مول العرب - 6 أكتوبر", "cancelled", 10, 26000),
            ("ORD-2026-05-0015", "حائط ميديا للمعرض", "أكاديمية المستقبل", "قاعة Cairo ICT", "closed", -10, 99000),
        ]
        item_cycle = [
            [("LED-P3-IN", 24), ("SPK-1000W", 4), ("MIC-WL-SET", 2), ("LGT-PAR", 8), ("PLY-MEDIA", 1)],
            [("LED-P4-OUT", 18), ("SND-MIX12", 1), ("SPK-1000W", 6), ("LGT-MH", 4), ("GEN-30KVA", 1)],
            [("WOOD-BOOTH-M", 20), ("TBL-EVENT", 8), ("DSP-55", 4), ("CBL-HDMI", 10)],
        ]
        orders = {}
        for idx, (code, title, client_name, location, status, days, revenue) in enumerate(specs):
            start = self.aware(days, 9)
            end = start + timedelta(days=1, hours=10)
            order = Order.objects.create(
                code=code,
                client=clients[client_name],
                title=title,
                event_location=location,
                start_at=start,
                end_at=end,
                status=status,
                payment_status="unpaid",
                revenue_amount=Decimal(revenue),
                total_amount=Decimal(revenue),
                notes="طلب تجريبي يعكس دورة العمل: عرض سعر، توفر مخزون، تنفيذ، مصروفات، وتحصيل.",
                created_by=users[ROLE_SALES],
            )
            orders[code] = order
            JobSchedule.objects.create(
                order=order,
                setup_start_at=start - timedelta(hours=8),
                setup_end_at=start - timedelta(hours=2),
                dismantle_start_at=end,
                dismantle_end_at=end + timedelta(hours=5),
                status="scheduled",
                notes="جدولة تركيب وفك حسب خطة التشغيل.",
            )
            OrderStatusHistory.objects.create(
                order=order,
                from_status="",
                to_status=status,
                changed_by=users[ROLE_OPERATIONS],
                notes="حالة تجريبية لدورة حياة الطلب.",
            )
            for sku, qty in item_cycle[idx % len(item_cycle)]:
                item = items[sku]
                OrderItem.objects.create(
                    order=order,
                    item=item,
                    description=f"تأجير {item.name}",
                    quantity=qty,
                    unit_price=item.rental_price,
                    cost_price=item.replacement_cost,
                )
                if status in ["confirmed", "scheduled", "in_progress", "installed", "event_running"]:
                    ItemReservation.objects.create(
                        item=item,
                        order=order,
                        quantity=min(qty, item.available_quantity),
                        start_at=start,
                        end_at=end,
                        status="reserved",
                    )
            tech = staff["يوسف نبيل"] if idx % 2 == 0 else staff["محمود رضا"]
            JobStaffAssignment.objects.create(
                order=order,
                staff=tech,
                role="تركيب وتشغيل",
                scheduled_start_at=start - timedelta(hours=8),
                scheduled_end_at=end,
                cost=Decimal("2600") + idx * Decimal("100"),
                status="completed" if days < 0 else "assigned",
            )
            JobTask.objects.create(
                order=order,
                assigned_to=tech,
                title=f"تجهيز وتركيب {title}",
                due_at=start - timedelta(hours=3),
                status="done" if days < 0 else "todo",
                notes="مراجعة المعدات وتجربة التشغيل قبل تسليم الموقع.",
            )
            vendor = list(vendors.values())[idx % len(vendors)]
            JobVendorAssignment.objects.create(
                order=order,
                vendor=vendor,
                service_description=f"دعم خارجي لطلب {title}",
                cost=Decimal("4500") + idx * Decimal("500"),
                status="assigned",
            )
            driver = list(drivers.values())[idx % len(drivers)]
            JobDriverAssignment.objects.create(
                order=order,
                driver=driver,
                pickup_location="المخزن الرئيسي - مدينة نصر",
                dropoff_location=location,
                scheduled_at=start - timedelta(hours=10),
                cost=driver.day_rate,
                status="completed" if days < 0 else "assigned",
            )
            DriverTrip.objects.create(
                driver=driver,
                order=order,
                pickup_location="المخزن الرئيسي - مدينة نصر",
                dropoff_location=location,
                scheduled_at=start - timedelta(hours=10),
                status="completed" if days < 0 else "scheduled",
                cost=driver.day_rate,
                notes="رحلة نقل معدات للفعالية.",
            )
        return orders

    def seed_quotations(self, users, clients, items):
        rows = [
            ("QTN-2026-05-0001", "عرض تجهيز مؤتمر طبي", "دلتا فارما", "draft", 18),
            ("QTN-2026-05-0002", "عرض بوث معرض تعليمي", "جامعة المستقبل الخاصة", "sent", 21),
            ("QTN-2026-05-0003", "عرض نظام صوت وإضاءة", "قاعة النور للاحتفالات", "accepted", 12),
            ("QTN-2026-05-0004", "عرض شاشة خارجية لحملة تسويق", "شركة القناة للدعاية", "rejected", 9),
            ("QTN-2026-05-0005", "عرض تجهيز جناح معرض", "وكالة سمارت إكسبو", "converted_to_order", 25),
            ("QTN-2026-05-0006", "عرض منتهي لفعالية صغيرة", "شركة الأهرام للتسويق", "expired", -2),
        ]
        for idx, (code, title, client_name, status, days) in enumerate(rows, start=1):
            q = Quotation.objects.create(
                code=code,
                client=clients[client_name],
                title=title,
                status=status,
                valid_until=timezone.localdate() + timedelta(days=max(days, 1)),
                event_start_at=self.aware(days, 10),
                event_end_at=self.aware(days + 1, 22),
                subtotal=Decimal("45000") + idx * Decimal("9000"),
                discount_amount=Decimal("1500"),
                total_amount=Decimal("43500") + idx * Decimal("9000"),
                notes="عرض سعر تجريبي باللغة العربية مع بنود شاشة وصوت.",
                created_by=users[ROLE_SALES],
            )
            QuotationItem.objects.create(
                quotation=q,
                item=items["LED-P3-IN"],
                description="باقة شاشة LED داخلية",
                quantity=12,
                unit_price=items["LED-P3-IN"].rental_price,
                cost_price=items["LED-P3-IN"].replacement_cost,
                line_total=Decimal("7800"),
            )
            QuotationItem.objects.create(
                quotation=q,
                item=items["SPK-1000W"],
                description="باقة صوتيات للقاعة",
                quantity=4,
                unit_price=items["SPK-1000W"].rental_price,
                cost_price=items["SPK-1000W"].replacement_cost,
                line_total=Decimal("2800"),
            )

    def seed_invoices(self, users, orders):
        invoices = {}
        invoice_statuses = ["paid", "partially_paid", "issued", "overdue", "draft", "cancelled"]
        for idx, order in enumerate(list(orders.values())[:12], start=1):
            status = invoice_statuses[idx % len(invoice_statuses)]
            invoice = Invoice.objects.create(
                code=f"INV-2026-05-{idx:04d}",
                client=order.client,
                order=order,
                issue_date=(order.start_at - timedelta(days=2)).date(),
                due_date=(order.start_at + timedelta(days=7)).date(),
                status=status,
                subtotal=order.total_amount,
                total_amount=order.total_amount,
                created_by=users[ROLE_ACCOUNTANT],
                notes="فاتورة تجريبية من دورة حسابات العملاء.",
            )
            InvoiceItem.objects.create(
                invoice=invoice,
                description=order.title,
                quantity=1,
                unit_price=order.total_amount,
                line_total=order.total_amount,
            )
            invoices[order.code] = invoice
        return invoices

    def seed_payments(self, users, orders, invoices, methods, cashboxes, bank):
        payment_plan = {
            "ORD-2026-05-0001": [(1, "تحويل بنكي", "تحويل بنكي")],
            "ORD-2026-05-0002": [(1, "نقدي", "دفعة نقدية من العميل")],
            "ORD-2026-05-0003": [(Decimal("0.55"), "إنستاباي", "دفعة إنستاباي من العميل")],
            "ORD-2026-05-0004": [(Decimal("0.30"), "شيك", "شيك دفعة مقدمة")],
            "ORD-2026-05-0009": [(Decimal("0.50"), "فودافون كاش", "دفعة جزئية من العميل")],
            "ORD-2026-05-0011": [(Decimal("0.80"), "تحويل بنكي", "تحويل بنكي")],
            "ORD-2026-05-0015": [(1, "تحويل بنكي", "تحويل بنكي نهائي")],
        }
        for code, rows in payment_plan.items():
            order = orders[code]
            invoice = invoices.get(code)
            paid = Decimal("0")
            for fraction, method_name, note in rows:
                amount = (order.total_amount * Decimal(fraction)).quantize(Decimal("0.01"))
                paid += amount
                method = methods[method_name]
                Payment.objects.create(
                    client=order.client,
                    order=order,
                    invoice=invoice,
                    amount=amount,
                    payment_date=timezone.localdate() - timedelta(days=2),
                    method=method,
                    cashbox=cashboxes["الخزنة الرئيسية"] if method.method_type == "cash" else None,
                    bank_account=bank if method.method_type in ["bank", "cheque"] else None,
                    reference=f"COL-{code}-{method.id}",
                    notes=note,
                    created_by=users[ROLE_ACCOUNTANT],
                )
                if method.method_type == "cash":
                    CashTransaction.objects.create(
                        cashbox=cashboxes["الخزنة الرئيسية"],
                        transaction_type="in",
                        amount=amount,
                        transaction_date=timezone.localdate(),
                        description=f"دفعة نقدية من العميل {order.client.name} عن {code}",
                        order=order,
                        created_by=users[ROLE_CASHIER],
                    )
            if paid >= order.total_amount:
                order.payment_status = "fully_paid"
            elif paid:
                order.payment_status = "partially_paid"
            else:
                order.payment_status = "unpaid"
            order.save(update_fields=["payment_status", "updated_at"])

    def seed_expenses(self, users, orders, vendors, cashboxes):
        categories = {
            name: ExpenseCategory.objects.create(name=name, requires_approval_above=Decimal(limit))
            for name, limit in [
                ("مصروف تشغيل", 5000),
                ("دفعة مورد", 25000),
                ("تكلفة نقل", 5000),
                ("سلفة موظف", 3000),
                ("إيجار مولد", 12000),
                ("شراء كابلات", 2500),
                ("مصروف ضيافة", 5000),
                ("تكلفة فنيين", 8000),
                ("تأجير شاشات", 25000),
                ("تكلفة أعمال خشبية", 15000),
            ]
        }
        descriptions = [
            "مصروف تشغيل للموقع",
            "دفعة مورد",
            "تكلفة نقل معدات",
            "سلفة موظف",
            "إيجار مولد",
            "شراء كابلات",
            "مصروف ضيافة",
            "تكلفة فنيين",
        ]
        for idx, order in enumerate(orders.values(), start=1):
            category = list(categories.values())[idx % len(categories)]
            vendor = list(vendors.values())[idx % len(vendors)]
            amount = Decimal("1200") + idx * Decimal("450")
            Expense.objects.create(
                category=category,
                order=order,
                vendor=vendor if idx % 2 else None,
                amount=amount,
                expense_date=order.start_at.date(),
                description=f"{descriptions[idx % len(descriptions)]} - {order.code}",
                status="approved",
                created_by=users[ROLE_ACCOUNTANT],
            )
            if idx <= 8:
                CashTransaction.objects.create(
                    cashbox=cashboxes["عهدة التشغيل"],
                    transaction_type="out",
                    amount=amount,
                    transaction_date=order.start_at.date(),
                    description=f"صرف عهدة: {category.name} / {order.code}",
                    order=order,
                    created_by=users[ROLE_CASHIER],
                )

    def seed_vendor_driver_settlements(self, users, orders, vendors, drivers):
        for idx, order in enumerate(orders.values(), start=1):
            vendor = list(vendors.values())[idx % len(vendors)]
            cost = Decimal("5000") + idx * Decimal("650")
            VendorTransaction.objects.create(
                vendor=vendor,
                order=order,
                transaction_type="cost",
                amount=cost,
                description=f"تكلفة مورد عن الطلب {order.code}",
                transaction_date=order.start_at.date(),
                created_by=users[ROLE_ACCOUNTANT],
            )
            if idx % 3 != 0:
                VendorPayment.objects.create(
                    vendor=vendor,
                    order=order,
                    amount=(cost * Decimal("0.60")).quantize(Decimal("0.01")),
                    payment_date=timezone.localdate(),
                    method="نقدي",
                    reference=f"VP-{order.code}",
                    notes="دفعة مورد جزئية",
                    created_by=users[ROLE_ACCOUNTANT],
                )
        for idx, driver in enumerate(drivers.values(), start=1):
            DriverPayment.objects.create(
                driver=driver,
                amount=Decimal("1500") + idx * Decimal("300"),
                payment_date=timezone.localdate(),
                method="نقدي",
                reference=f"DP-2026-05-{idx}",
                created_by=users[ROLE_ACCOUNTANT],
            )

    def seed_cashbox_movements(self, users, cashboxes, orders):
        first_order = list(orders.values())[0]
        CashTransaction.objects.create(
            cashbox=cashboxes["الخزنة الرئيسية"],
            transaction_type="in",
            amount=Decimal("20000"),
            transaction_date=timezone.localdate(),
            description="توريد نقدية افتتاحية من الإدارة",
            created_by=users[ROLE_CASHIER],
        )
        CashTransaction.objects.create(
            cashbox=cashboxes["عهدة التشغيل"],
            transaction_type="out",
            amount=Decimal("1800"),
            transaction_date=timezone.localdate(),
            description="سلفة موظف لفريق الفنيين",
            created_by=users[ROLE_CASHIER],
            requires_approval=True,
        )
        CashTransaction.objects.create(
            cashbox=cashboxes["عهدة التشغيل"],
            transaction_type="out",
            amount=Decimal("900"),
            transaction_date=timezone.localdate(),
            description="شراء كابلات HDMI طارئة",
            order=first_order,
            created_by=users[ROLE_CASHIER],
        )
        CashTransaction.objects.create(
            cashbox=cashboxes["الخزنة الرئيسية"],
            transaction_type="in",
            amount=Decimal("500"),
            transaction_date=timezone.localdate(),
            description="تسوية فرق خزينة",
            created_by=users[ROLE_CASHIER],
            requires_approval=True,
        )

    def seed_payroll(self, users, staff):
        today = timezone.localdate()
        periods = [
            PayrollPeriod.objects.create(
                name="رواتب أبريل 2026",
                start_date=today.replace(month=4, day=1),
                end_date=today.replace(month=4, day=30),
                status="paid",
                approved_by=users[ROLE_OWNER],
                paid_at=timezone.now() - timedelta(days=12),
            ),
            PayrollPeriod.objects.create(
                name="رواتب مايو 2026",
                start_date=today.replace(day=1),
                end_date=today.replace(day=28),
                status="calculated",
            ),
        ]
        for period in periods:
            for idx, member in enumerate(staff.values(), start=1):
                bonus = Decimal("600") if idx % 2 == 0 else Decimal("0")
                deduction = Decimal("250") if idx % 3 == 0 else Decimal("0")
                advance = Decimal("1000") if idx in [2, 3] else Decimal("0")
                net = member.base_salary + bonus - deduction - advance
                line_status = "paid" if period.status == "paid" else "calculated"
                PayrollLine.objects.create(
                    period=period,
                    staff=member,
                    base_salary=member.base_salary,
                    task_pay=Decimal("0"),
                    advances=advance,
                    bonuses=bonus,
                    deductions=deduction,
                    net_pay=net,
                    paid_amount=net if period.status == "paid" else Decimal("0"),
                    status=line_status,
                )
                if advance and period == periods[1]:
                    StaffAdvance.objects.create(
                        staff=member,
                        amount=advance,
                        advance_date=today,
                        notes="سلفة من راتب مايو",
                        created_by=users[ROLE_ACCOUNTANT],
                    )
                if bonus:
                    StaffBonus.objects.create(
                        staff=member,
                        amount=bonus,
                        bonus_date=today,
                        reason="مكافأة ساعات إضافية في فعالية",
                        created_by=users[ROLE_ACCOUNTANT],
                    )
                if deduction:
                    StaffDeduction.objects.create(
                        staff=member,
                        amount=deduction,
                        deduction_date=today,
                        reason="خصم حضور",
                        created_by=users[ROLE_ACCOUNTANT],
                    )

    def seed_notifications(self, users):
        notes = [
            (users[ROLE_ACCOUNTANT], "مدفوعات عميل متأخرة", "توجد فاتورة مستحقة لمؤتمر حكومي لم يتم تحصيلها بالكامل."),
            (users[ROLE_OPERATIONS], "طلب مجدول غداً", "يبدأ تركيب الاجتماع السنوي لشركة النيل صباح الغد."),
            (users[ROLE_ACCOUNTANT], "دفعة مورد مستحقة", "مورد برايت لتأجير الشاشات لديه مستحقات مفتوحة."),
            (users[ROLE_OPERATIONS], "تنبيه توفر مخزون", "كمية شاشات LED الداخلية المحجوزة مرتفعة هذا الأسبوع."),
            (users[ROLE_OWNER], "اعتماد رواتب مطلوب", "رواتب مايو 2026 محسوبة وتحتاج إلى اعتماد."),
            (users[ROLE_CASHIER], "إغلاق عهدة التشغيل", "عهدة التشغيل تحتاج مراجعة وإغلاق نهاية الشهر."),
        ]
        for user, title, message in notes:
            Notification.objects.create(user=user, title=title, message=message)
