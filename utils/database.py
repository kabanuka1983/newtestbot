from aiogram.types import User, Message
from gino import Gino
from sqlalchemy import sql, Column, Integer, Sequence, BigInteger, String, Date, Boolean

from data.config import DB_USER, DB_PASS, HOST, DB_NAME

db = Gino()


# class Users(db.Model):
#     __tablename__ = 'users'
#     query: sql.Select
#     update: sql.Select
#
#     id = Column(Integer, Sequence('dish_id_seq'), primary_key=True)
#     user_id = Column
#     date = Column(Date)
#     name = Column(String(100))
#     price = Column(Integer)
#
#     def __repr__(self):
#         return f"<Dish(name='{self.name}', price='{self.price}')>"


class Customer(db.Model):
    __tablename__ = 'customers'
    query: sql.Select

    id = Column(Integer, Sequence('customer_id_seq'), primary_key=True)
    customer_id = Column(BigInteger, Sequence('customer_name_app_seq'), primary_key=True)
    pseudonym = Column(String(100))
    age = Column(Integer)
    location = Column(String(100))
    username = Column(String(100))
    full_name = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    subs_before = Column(Integer)
    subs_check = Column(Boolean)

    def __repr__(self):
        return f"<Customer(id='{self.id}', full_name='{self.full_name}', " \
               f"pseudonym='{self.pseudonym}', credit='{self.credit}')>"


class DBCommands:
    @staticmethod
    async def get_customer(customer_id):
        customer = await Customer.query.where(Customer.customer_id == customer_id).gino.first()
        return customer

    async def add_new_customer(self, message: Message, date):
        old_customer = await self.get_customer(message.from_user.id)
        if old_customer:
            return
        new_customer = Customer()
        new_customer.customer_id = message.from_user.id
        new_customer.full_name = message.from_user.full_name
        new_customer.first_name = message.from_user.first_name
        new_customer.last_name = message.from_user.last_name
        new_customer.username = message.from_user.username
        new_customer.phone_number = message.contact.phone_number
        new_customer.subs_before = date
        new_customer.subs_check = False
        await new_customer.create()
        return new_customer

    # @staticmethod
    # async def get_dishes():
    #     dishes = await Dish.query.gino.all()
    #     return dishes

    # @staticmethod
    # async def get_menu_date():
    #     dish = await Dish.query.gino.first()
    #     return dish.date

    @staticmethod
    async def get_customers():
        customers = await Customer.query.gino.all()
        return customers

    # @staticmethod
    # async def get_customer_by_pseudonym(pseudonym):
    #     customer = await Customer.query.where(Customer.pseudonym == pseudonym).gino.first()
    #     return customer

    @staticmethod
    async def update_fin_registration(customer_id, pseudonym, age, location):
        await Customer.update.values(pseudonym=pseudonym,
                                     age=age,
                                     location=location,
                                     subs_check=True).where(Customer.customer_id == customer_id).gino.status()

    @staticmethod
    async def update_subs_before(customer_id, subs_before):
        await Customer.update.values(subs_before=subs_before).where(Customer.customer_id == customer_id).gino.status()

    # @staticmethod
    # async def delete_item(dish_name):
    #     await Dish.delete.where(Dish.name == dish_name).gino.status()

    # @staticmethod
    # async def update_price(dish_name, new_price):
    #     await Dish.update.values(price=new_price).where(Dish.name == dish_name).gino.status()

    # @staticmethod
    # async def del_dish_table():
    #     await Dish.delete.gino.all()

    @staticmethod
    async def set_current_order(customer: Customer):
        await Customer.update.values(current_order=1).where(Customer.customer_id == customer.customer_id).gino.status()

    @staticmethod
    async def cancel_current_order():
        await Customer.update.values(current_order=0).gino.status()

    @staticmethod
    async def update_pseudonym(customer, pseudonym):
        await Customer.update.values(pseudonym=pseudonym).\
            where(Customer.customer_id == customer.customer_id).gino.status()

    async def credit_up(self, customer_id, val: int, customer_id_is_pseudonym=False):
        if customer_id_is_pseudonym:
            customer = await self.get_customer_bypseudonym(pseudonym=customer_id)
        else:
            customer = await self.get_customer(customer_id=customer_id)
        new_credit = int(customer.credit) + val
        await Customer.update.values(credit=new_credit).where(
            Customer.customer_id == customer.customer_id).gino.status()
        return customer

    async def credit_down(self, customer_id, val: int):
        customer = await self.get_customer(customer_id=customer_id)
        new_credit = int(customer.credit) - val
        await Customer.update.values(credit=new_credit).where(
            Customer.customer_id == customer.customer_id).gino.status()


async def create_db():
    await db.set_bind(f"postgres://{DB_USER}:{DB_PASS}@{HOST}/{DB_NAME}")
    await db.gino.drop_all()
    await db.gino.create_all()

