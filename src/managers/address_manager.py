from config import Config
from utils import rsa_encrypt, rsa_decrypt
from managers.base_manager import BaseManager
from entities.address import Address


class AddressManager(BaseManager):
    def __init__(self, config: Config):
        super().__init__(config)

    def initialize(self):
        SQL_CREATE_ADDRESS_TABLE = """
            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY,
                street_name TEXT NOT NULL,
                house_number TEXT NOT NULL,
                zip_code TEXT NOT NULL,
                city TEXT NOT NULL,
                member_id INTEGER NOT NULL,
                FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
            );
        """

        try:
            cursor = self.config.con.cursor()
            cursor.execute(SQL_CREATE_ADDRESS_TABLE)
            self.config.con.commit()
        finally:
            cursor.close()

    def seed_addresses(self):
        addresses = [
            {
                "street_name": "Langestraat",
                "house_number": "12A",
                "zip_code": "1234 AB",
                "city": "Amsterdam",
                "member_id": 1,
            },
            {
                "street_name": "Hoofdweg",
                "house_number": "34",
                "zip_code": "2345 BC",
                "city": "Utrecht",
                "member_id": 2,
            },
        ]

        for address in addresses:
            encrypted_street_name = rsa_encrypt(address["street_name"], self.config.public_key)
            encrypted_house_number = rsa_encrypt(address["house_number"], self.config.public_key)
            encrypted_zip_code = rsa_encrypt(address["zip_code"], self.config.public_key)
            encrypted_city = rsa_encrypt(address["city"], self.config.public_key)

            SQL_CREATE_ADDRESSES = (
                "INSERT INTO addresses (street_name, house_number, zip_code, city, member_id) VALUES (?, ?, ?, ?, ?);"
            )

            try:
                cursor = self.config.con.cursor()
                cursor.execute(
                    SQL_CREATE_ADDRESSES,
                    (
                        encrypted_street_name,
                        encrypted_house_number,
                        encrypted_zip_code,
                        encrypted_city,
                        f"{address['member_id']}",
                    ),
                )
                self.config.con.commit()
            finally:
                cursor.close()

    def get_addresses(self) -> list[Address]:
        SQL_SELECT_ADDRESSES = "SELECT * FROM addresses;"
        try:
            cursor = self.config.con.cursor()
            cursor.execute(SQL_SELECT_ADDRESSES)
            result = cursor.fetchall()
        finally:
            cursor.close()

        addresses = []
        for address_data in result:
            address = Address(*address_data)
            address.street_name = rsa_decrypt(address.street_name, self.config.private_key)
            address.house_number = rsa_decrypt(address.house_number, self.config.private_key)
            address.zip_code = rsa_decrypt(address.zip_code, self.config.private_key)
            address.city = rsa_decrypt(address.city, self.config.private_key)
            addresses.append(address)

        return addresses

    def get_address(self, member_id: int) -> Address:
        for address in self.get_addresses():
            if address.member_id == member_id:
                return address
        return None

    def create_address(
        self,
        street_name: str,
        house_number: str,
        zip_code: str,
        city: str,
        member_id: int,
    ) -> Address:
        SQL_CREATE_ADDRESS = (
            "INSERT INTO addresses (street_name, house_number, zip_code, city, member_id) VALUES (?, ?, ?, ?, ?);"
        )

        encrypted_street_name = rsa_encrypt(street_name, self.config.public_key)
        encrypted_house_number = rsa_encrypt(house_number, self.config.public_key)
        encrypted_zip_code = rsa_encrypt(zip_code, self.config.public_key)
        encrypted_city = rsa_encrypt(city, self.config.public_key)

        try:
            cursor = self.config.con.cursor()
            cursor.execute(
                SQL_CREATE_ADDRESS,
                (
                    encrypted_street_name,
                    encrypted_house_number,
                    encrypted_zip_code,
                    encrypted_city,
                    member_id,
                ),
            )
            self.config.con.commit()
        finally:
            cursor.close()

        return self.get_address(cursor.lastrowid)

    def update_address(
        self,
        address: Address,
        street_name: str,
        house_number: str,
        zip_code: str,
        city: str,
        member_id: int,
    ):
        encrypted_street_name = rsa_encrypt(street_name, self.config.public_key)
        encrypted_house_number = rsa_encrypt(house_number, self.config.public_key)
        encrypted_zip_code = rsa_encrypt(zip_code, self.config.public_key)
        encrypted_city = rsa_encrypt(city, self.config.public_key)

        SQL_UPDATE_ADDRESS = (
            "UPDATE addresses SET street_name = ?, house_number = ?, zip_code = ?, city = ? WHERE member_id = ?;"
        )
        try:
            cursor = self.config.con.cursor()
            cursor.execute(
                SQL_UPDATE_ADDRESS,
                (
                    encrypted_street_name,
                    encrypted_house_number,
                    encrypted_zip_code,
                    encrypted_city,
                    member_id,
                ),
            )
            self.config.con.commit()
        finally:
            cursor.close()

        return self.get_address(address.id)
