"""
Task 3: Object-Oriented Application Design
Author: sneb18240602
Description: Refactoring the record system into an object-oriented architecture
             using classes: User, Record, FileManager, ReportGenerator, and Manager.
"""

import json
import os

class User:
    """Represents an application user (e.g., Donor, Volunteer)."""
    def __init__(self, user_id: str, name: str, role: str, status: str = "Active"):
        self.user_id = user_id
        self.name = name
        self.role = role
        self.status = status

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "role": self.role,
            "status": self.status
        }

    def display(self) -> None:
        print("User Created")
        print("----------------")
        print(f"ID: {self.user_id}")
        print(f"Name: {self.name}")
        print(f"Role: {self.role}")
        print(f"Status: {self.status}\n")


class Record:
    """Represents a surplus item or resource record."""
    def __init__(self, record_id: str, name: str, category: str, quantity: int, location: str, status: str = "Available"):
        self.record_id = record_id
        self.name = name
        self.category = category
        self.quantity = quantity
        self.location = location
        self.status = status

    def to_dict(self) -> dict:
        return {
            "id": self.record_id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "location": self.location,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            record_id=data.get("id", ""),
            name=data.get("name", ""),
            category=data.get("category", ""),
            quantity=int(data.get("quantity", 0)),
            location=data.get("location", ""),
            status=data.get("status", "Available")
        )


class FileManager:
    """Handles persistent file storage and safe reading/writing."""
    def __init__(self, filename: str = "records_oop.json"):
        self.filename = filename

    def load_data(self) -> list:
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            print(f"Warning: '{self.filename}' was corrupted or empty. Initializing empty dataset.")
            return []

    def save_data(self, data: list) -> bool:
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except OSError as e:
            print(f"Error saving to file: {e}")
            return False


class ReportGenerator:
    """Handles generation of summaries and formatted tabular views."""
    @staticmethod
    def print_summary(records: list) -> None:
        print("\n--- System Summary Report ---")
        total_records = len(records)
        total_qty = sum(r.quantity for r in records)
        available_count = sum(1 for r in records if r.status.lower() == "available")
        claimed_count = sum(1 for r in records if r.status.lower() == "claimed")

        print(f"Total Records: {total_records}")
        print(f"Total Quantity: {total_qty}")
        print(f"Available Records: {available_count}")
        print(f"Claimed Records: {claimed_count}")

    @staticmethod
    def print_table(records: list) -> None:
        if not records:
            print("No records found.")
            return
        print(f"\n{'ID':<8} | {'Name':<20} | {'Category':<15} | {'Quantity':<10} | {'Location':<15} | {'Status':<10}")
        print("-" * 88)
        for r in records:
            print(f"{r.record_id:<8} | {r.name:<20} | {r.category:<15} | {r.quantity:<10} | {r.location:<15} | {r.status:<10}")


class RecordManager:
    """Central manager coordinating records and file storage."""
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.records = [Record.from_dict(d) for d in self.file_manager.load_data()]

    def _generate_id(self) -> str:
        nums = []
        for r in self.records:
            if r.record_id.startswith("FD") and r.record_id[2:].isdigit():
                nums.append(int(r.record_id[2:]))
        next_val = max(nums, default=0) + 1
        return f"FD{next_val:03d}"

    def add_record(self, name: str, category: str, quantity: int, location: str, status: str = "Available") -> None:
        new_id = self._generate_id()
        record = Record(new_id, name, category, quantity, location, status)
        self.records.append(record)
        self.file_manager.save_data([r.to_dict() for r in self.records])
        print(f"\nRecord Added Successfully")
        print(f"ID: {record.record_id}")
        print(f"Status: {record.status}")

    def get_all(self) -> list:
        return self.records

    def search(self, query: str) -> list:
        q = query.lower()
        return [r for r in self.records if q in r.record_id.lower() or q in r.name.lower() or q in r.category.lower()]

    def update_record(self, record_id: str, **kwargs) -> bool:
        record = next((r for r in self.records if r.record_id.upper() == record_id.upper()), None)
        if not record:
            return False
        for key, val in kwargs.items():
            if val is not None and hasattr(record, key):
                setattr(record, key, val)
        self.file_manager.save_data([r.to_dict() for r in self.records])
        return True


def main():
    # Demonstrating the User entity matching the assignment sample
    sample_user = User("U001", "Krishna", "Donor", "Active")
    sample_user.display()

    file_mgr = FileManager("records_oop.json")
    manager = RecordManager(file_mgr)

    # Pre-populate sample records if empty
    if not manager.get_all():
        manager.add_record("Vegetable Rice", "Food", 20, "Mumbai", "Available")
        manager.add_record("Bread", "Bakery", 10, "Pune", "Claimed")

    while True:
        print("\n=== OOP Record Management System ===")
        print("1. Add Record")
        print("2. View All Records")
        print("3. Search Record")
        print("4. Update Record")
        print("5. Generate Summary")
        print("6. Exit")

        choice = input("Select an option (1-6): ").strip()
        if choice == "1":
            name = input("Enter Name: ").strip()
            category = input("Enter Category: ").strip()
            qty = int(input("Enter Quantity: ").strip() or "0")
            location = input("Enter Location: ").strip()
            status = input("Enter Status (Available/Claimed) [default: Available]: ").strip() or "Available"
            manager.add_record(name, category, qty, location, status)
        elif choice == "2":
            ReportGenerator.print_table(manager.get_all())
        elif choice == "3":
            q = input("Enter search term: ").strip()
            results = manager.search(q)
            ReportGenerator.print_table(results)
        elif choice == "4":
            r_id = input("Enter ID to update (e.g., FD001): ").strip()
            name = input("New Name (leave blank to keep): ").strip() or None
            status = input("New Status (leave blank to keep): ").strip() or None
            success = manager.update_record(r_id, name=name, status=status)
            if success:
                print(f"Record {r_id} updated successfully.")
            else:
                print(f"Record {r_id} not found.")
        elif choice == "5":
            ReportGenerator.print_summary(manager.get_all())
        elif choice == "6":
            print("Exiting application.")
            break
        else:
            print("Invalid option. Please choose between 1 and 6.")


if __name__ == "__main__":
    main()
