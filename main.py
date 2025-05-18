import streamlit as st
import json
from datetime import datetime
from abc import ABC, abstractmethod
import os
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide"
)

# Constants
SELECT_ITEM_LABEL = "Select Item"
DEFAULT_FILENAME = "inventory_data.json"

# Custom CSS - Soft Pastel Theme
st.markdown("""
<style>
    body {
        background-color: #FFF9F0;
        color: #3E3E3E;
    }

    .main-title {
        font-size: 3rem;
        color: #6A5ACD;
        text-align: center;
        padding: 1rem;
        border-bottom: 2px solid #B0C4DE;
        margin-bottom: 2rem;
        font-family: 'Segoe UI', sans-serif;
    }

    .section-header {
        font-size: 2.4rem;
        font-weight: bold;
        color: #483D8B;
        text-align: center;
        padding: 0.6rem;
        background-color: #E6E6FA;
        border-radius: 6px;
        margin: 2rem 0 1rem 0;
    }

    .sub-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #34495E;
        padding: 0.4rem 0;
        margin: 1rem 0;
        border-left: 4px solid #3498DB;
    }

    .item-card {
        font-size: 1.4rem;
        font-weight: bold;
        text-align: left;
        color: #2C3E50;
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 6px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #3498DB;
        margin-bottom: 0.8rem;
    }

    .metric-box {
        font-size: 2.8rem;
        font-weight: bold;
        text-align: center;
        color: #2980B9;
        background-color: #F2F6FB;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }

    .sidebar-title {
        font-size: 2rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        padding: 0.8rem;
        border-bottom: 1px solid #DDE2E6;
        margin-bottom: 1.2rem;
    }

    .success-message {
        color: #27AE60;
        font-weight: bold;
    }

    .warning-message {
        color: #F39C12;
        font-weight: bold;
    }

    .error-message {
        color: #E74C3C;
        font-weight: bold;
    }

    .info-banner {
        font-size: 1.6rem;
        font-weight: bold;
        text-align: center;
        color: #2C3E50;
        background-color: #EBF5FB;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #3498DB;
        margin: 1rem 0;
    }

    .warn-banner {
        font-size: 1.6rem;
        font-weight: bold;
        color: #E67E22;
        background-color: #FFF5E4;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #F39C12;
        margin: 1rem 0;
    }

    .stButton>button {
        background-color: #3498DB;
        color: white;
        font-weight: bold;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
    }

    .stTextInput input,
    .stNumberInput input,
    .stSelectbox select {
        background-color: #FFFFFF;
        color: #333333;
        border: 1px solid #CCCCCC;
    }

    .stDataFrame {
        background-color: #FFFFFF;
        border: 1px solid #DDDDDD;
        border-radius: 6px;
    }

    .stForm {
        background-color: #FAFAFA;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #EEEEEE;
    }

    .stMetric {
        background-color: #F2F6FB;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)


# Abstract Base Class: Item
class Item(ABC):
    def __init__(self, item_id, name, price, stock):
        self._id = item_id
        self._name = name
        self._price = price
        self._stock = stock

    def replenish(self, amount):
        if amount > 0:
            self._stock += amount
            return True
        return False

    def sell(self, quantity):
        if quantity <= self._stock and quantity > 0:
            self._stock -= quantity
            return True
        return False

    def total_value(self):
        return self._price * self._stock

    @abstractmethod
    def details(self):
        pass

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "id": self._id,
            "name": self._name,
            "price": self._price,
            "stock": self._stock
        }


# Subclasses
class Gadget(Item):
    def __init__(self, item_id, name, price, stock, warranty, brand):
        super().__init__(item_id, name, price, stock)
        self._warranty = warranty
        self._brand = brand

    def details(self):
        return f"Brand: {self._brand}, Warranty: {self._warranty} yrs"

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "warranty": self._warranty,
            "brand": self._brand
        })
        return data


class Food(Item):
    def __init__(self, item_id, name, price, stock, expiry):
        super().__init__(item_id, name, price, stock)
        self._expiry = expiry

    def is_expired(self):
        today = datetime.today().date()
        exp_date = datetime.strptime(self._expiry, "%Y-%m-%d").date()
        return today > exp_date

    def details(self):
        status = " (Expired)" if self.is_expired() else ""
        return f"Expiry: {self._expiry}{status}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"expiry": self._expiry})
        return data


class Apparel(Item):
    def __init__(self, item_id, name, price, stock, size, fabric):
        super().__init__(item_id, name, price, stock)
        self._size = size
        self._fabric = fabric

    def details(self):
        return f"Size: {self._size}, Fabric: {self._fabric}"

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "size": self._size,
            "fabric": self._fabric
        })
        return data


# Exceptions
class NotEnoughStock(Exception):
    pass


class DuplicateItem(Exception):
    pass


class InvalidEntry(Exception):
    pass


# Stock Manager
class StockManager:
    def __init__(self):
        self.items = {}

    def add_item(self, item):
        if item._id in self.items:
            raise DuplicateItem(f"Item ID {item._id} already exists")
        self.items[item._id] = item

    def remove_item(self, item_id):
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False

    def search_by_name(self, name):
        return [i for i in self.items.values() if name.lower() in i._name.lower()]

    def search_by_type(self, item_type):
        return [i for i in self.items.values() if i.__class__.__name__ == item_type]

    def list_all(self):
        return list(self.items.values())

    def sell_item(self, item_id, quantity):
        if item_id not in self.items:
            return False, "Item not found"
        item = self.items[item_id]
        if item._stock < quantity:
            return False, f"Not enough stock. Available: {item._stock}"
        item.sell(quantity)
        return True, f"Sold {quantity} units of {item._name}"

    def restock_item(self, item_id, quantity):
        if item_id not in self.items:
            return False, "Item not found"
        item = self.items[item_id]
        if quantity <= 0:
            return False, "Quantity must be positive"
        item.replenish(quantity)
        return True, f"Restocked {quantity} units of {item._name}"

    def total_value(self):
        return sum(item.total_value() for item in self.items.values())

    def remove_expired(self):
        expired = []
        for iid, item in list(self.items.items()):
            if isinstance(item, Food) and item.is_expired():
                expired.append(item._name)
                del self.items[iid]
        return expired

    def save_to_file(self, filename):
        try:
            data = [item.to_dict() for item in self.items.values()]
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True, "Saved successfully"
        except Exception as e:
            return False, str(e)

    def load_from_file(self, filename):
        try:
            if not os.path.exists(filename):
                return False, f"File not found: {filename}"
            with open(filename, 'r') as f:
                data = json.load(f)
            self.items.clear()
            for entry in data:
                t = entry["type"]
                if t == "Gadget":
                    item = Gadget(entry["id"], entry["name"], entry["price"], entry["stock"], entry["warranty"], entry["brand"])
                elif t == "Food":
                    item = Food(entry["id"], entry["name"], entry["price"], entry["stock"], entry["expiry"])
                elif t == "Apparel":
                    item = Apparel(entry["id"], entry["name"], entry["price"], entry["stock"], entry["size"], entry["fabric"])
                else:
                    continue
                self.items[item._id] = item
            return True, "Loaded successfully"
        except Exception as e:
            return False, str(e)


# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = StockManager()

if 'msg' not in st.session_state:
    st.session_state.msg = None

if 'msg_type' not in st.session_state:
    st.session_state.msg_type = None


def show_message():
    if st.session_state.msg:
        if st.session_state.msg_type == "success":
            st.success(st.session_state.msg)
        elif st.session_state.msg_type == "error":
            st.error(st.session_state.msg)
        elif st.session_state.msg_type == "info":
            st.info(st.session_state.msg)
        elif st.session_state.msg_type == "warning":
            st.warning(st.session_state.msg)
        st.session_state.msg = None
        st.session_state.msg_type = None


def set_message(text, msg_type="info"):
    st.session_state.msg = text
    st.session_state.msg_type = msg_type


# Dashboard
def dashboard():
    st.markdown('<div class="section-header">Dashboard Overview</div>', unsafe_allow_html=True)
    manager = st.session_state.manager
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items", len(manager.list_all()))
    with col2:
        st.metric("Total Value", f"Rs. {manager.total_value():,.2f}")
    with col3:
        expired = len([i for i in manager.list_all() if isinstance(i, Food) and i.is_expired()])
        st.metric("Expired Items", expired)

    items = manager.list_all()
    if not items:
        st.markdown('<div class="info-banner">No items in inventory yet.</div>', unsafe_allow_html=True)
    else:
        df = pd.DataFrame([{
            "ID": i._id,
            "Name": i._name,
            "Type": type(i).__name__,
            "Price": f"Rs. {i._price:.2f}",
            "Stock": i._stock,
            "Details": i.details()
        } for i in items])
        st.dataframe(df, use_container_width=True)

    if st.button("Remove Expired Items"):
        removed = manager.remove_expired()
        if removed:
            set_message(f"Removed expired items: {', '.join(removed)}", "success")
        else:
            set_message("No expired items found", "info")
        st.rerun()


# Add Item
def add_item():
    st.markdown('<div class="section-header">Add New Item</div>', unsafe_allow_html=True)
    with st.form("add_form"):
        itype = st.selectbox("Item Type", ["Gadget", "Food", "Apparel"])
        iid = st.number_input("Item ID", min_value=1, step=1)
        name = st.text_input("Item Name")
        price = st.number_input("Price (Rs.)", min_value=0.01, step=0.01)
        stock = st.number_input("Stock Quantity", min_value=0, step=1)
        fields = {}
        if itype == "Gadget":
            fields['warranty'] = st.number_input("Warranty (years)", min_value=0, step=1)
            fields['brand'] = st.text_input("Brand")
        elif itype == "Food":
            fields['expiry'] = st.date_input("Expiry Date").strftime("%Y-%m-%d")
        elif itype == "Apparel":
            fields['size'] = st.text_input("Size")
            fields['fabric'] = st.text_input("Fabric")

        submitted = st.form_submit_button("Add Item")
        if submitted:
            try:
                manager = st.session_state.manager
                if itype == "Gadget":
                    item = Gadget(iid, name, price, stock, fields['warranty'], fields['brand'])
                elif itype == "Food":
                    item = Food(iid, name, price, stock, fields['expiry'])
                elif itype == "Apparel":
                    item = Apparel(iid, name, price, stock, fields['size'], fields['fabric'])
                manager.add_item(item)
                set_message(f"Added: {name}", "success")
                st.rerun()
            except DuplicateItem:
                set_message("Item ID already exists", "error")


# Manage Items
def manage_items():
    st.markdown('<div class="section-header">Manage Inventory</div>', unsafe_allow_html=True)
    manager = st.session_state.manager
    items = manager.list_all()
    if not items:
        st.markdown('<div class="info-banner">No items available. Please add one first.</div>', unsafe_allow_html=True)
        return

    tab1, tab2, tab3 = st.tabs(["Sell", "Replenish", "Remove"])
    with tab1:
        with st.form("sell_form"):
            options = {f"{i._id}: {i._name} (Stock: {i._stock})": i._id for i in items}
            selected = st.selectbox(SELECT_ITEM_LABEL, list(options.keys()))
            qty = st.number_input("Quantity", min_value=1, step=1)
            if st.form_submit_button("Sell"):
                success, msg = manager.sell_item(options[selected], qty)
                set_message(msg, "success" if success else "error")
                st.rerun()

    with tab2:
        with st.form("restock_form"):
            options = {f"{i._id}: {i._name}": i._id for i in items}
            selected = st.selectbox(SELECT_ITEM_LABEL, list(options.keys()))
            qty = st.number_input("Quantity to Add", min_value=1, step=1)
            if st.form_submit_button("Replenish"):
                success, msg = manager.restock_item(options[selected], qty)
                set_message(msg, "success" if success else "error")
                st.rerun()

    with tab3:
        with st.form("remove_form"):
            options = {f"{i._id}: {i._name}": i._id for i in items}
            selected = st.selectbox(SELECT_ITEM_LABEL, list(options.keys()))
            if st.form_submit_button("Remove"):
                if manager.remove_item(options[selected]):
                    set_message("Item removed", "success")
                else:
                    set_message("Error removing item", "error")
                st.rerun()


# Search
def search_items():
    st.markdown('<div class="section-header">Search Inventory</div>', unsafe_allow_html=True)
    manager = st.session_state.manager
    tab1, tab2 = st.tabs(["By Name", "By Type"])
    with tab1:
        name = st.text_input("Enter item name")
        if name:
            results = manager.search_by_name(name)
            if results:
                st.markdown(f'<div class="success-message">{len(results)} matches found</div>', unsafe_allow_html=True)
                for r in results:
                    st.markdown(f'<div class="item-card">{r._name} | {r.details()}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="warn-banner>No match found for "{name}"</div>', unsafe_allow_html=True)
    with tab2:
        itype = st.selectbox("Select Type", ["Gadget", "Food", "Apparel"])
        if st.button("Search"):
            results = manager.search_by_type(itype)
            if results:
                st.markdown(f'<div class="success-message">{len(results)} {itype}s found</div>', unsafe_allow_html=True)
                for r in results:
                    st.markdown(f'<div class="item-card">{r._name} | {r.details()}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="warn-banner>No {itype}s found</div>', unsafe_allow_html=True)


# Save/Load
def save_load():
    st.markdown('<div class="section-header">Save / Load Data</div>', unsafe_allow_html=True)
    manager = st.session_state.manager
    col1, col2 = st.columns(2)
    with col1:
        fname = st.text_input("Filename to Save", DEFAULT_FILENAME)
        if st.button("Save Inventory"):
            success, msg = manager.save_to_file(fname)
            set_message(msg, "success" if success else "error")
    with col2:
        fname = st.text_input("Filename to Load", DEFAULT_FILENAME)
        if st.button("Load Inventory"):
            success, msg = manager.load_from_file(fname)
            set_message(msg, "success" if success else "error")


# Main App
def main():
    st.markdown('<h1 class="main-title">📦 Smart Inventory Tracker</h1>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-title">Navigation</div>', unsafe_allow_html=True)
    page = st.sidebar.radio("Go to", ["Dashboard", "Add Item", "Manage Items", "Search", "Save/Load"])

    show_message()

    if page == "Dashboard":
        dashboard()
    elif page == "Add Item":
        add_item()
    elif page == "Manage Items":
        manage_items()
    elif page == "Search":
        search_items()
    elif page == "Save/Load":
        save_load()

    st.markdown("""
    <div style='text-align: center; margin-top: 40px; font-weight: bold;'>
        Made with ❤️ by Awais Mehmood
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
