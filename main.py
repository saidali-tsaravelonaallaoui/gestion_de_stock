import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.simpledialog
from database import Database
from utils import get_categories
import mysql.connector
from mysql.connector import Error
import csv

class StockManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Stock")

        # Instance de la classe Database
        self.db = Database()

        # Création des widgets
        self.create_widgets()

        # Affichage initial des produits
        self.show_products()

    def create_widgets(self):
        # Création du Treeview pour afficher les produits
        self.tree = ttk.Treeview(self.root, show="headings", columns=('ID', 'Nom', 'Description', 'Prix', 'Quantité', 'Catégorie'), displaycolumns=('ID', 'Nom', 'Description', 'Prix', 'Quantité', 'Catégorie'))
        self.tree.column('#1', width=50)
        self.tree.column('#2', width=150)
        self.tree.column('#3', width=250)
        self.tree.column('#4', width=80)
        self.tree.column('#5', width=80)
        self.tree.column('#6', width=90)
        
        
        self.tree.heading('#1', text='ID', anchor=tk.CENTER)
        self.tree.heading('#2', text='Nom')
        self.tree.heading('#3', text='Description', anchor=tk.CENTER)
        self.tree.heading('#4', text='Prix')
        self.tree.heading('#5', text='Quantité')
        self.tree.heading('#6', text='Catégorie')
        self.tree.pack(padx=10, pady=10)

        # Boutons pour ajouter, modifier, supprimer et exporter
        add_button = tk.Button(self.root, text="Ajouter Produit", command=self.add_product)
        add_button.pack(pady=5)
        
        update_button = tk.Button(self.root, text="Modifier", command=self.update_product)
        update_button.pack(pady=10)

        remove_button = tk.Button(self.root, text="Supprimer Produit", command=self.remove_product)
        remove_button.pack(pady=5)

        export_button = tk.Button(self.root, text="Exporter CSV", command=self.export_csv)
        export_button.pack(pady=5)

        # Filtrer par catégorie
        self.category_var = tk.StringVar()
        self.category_var.set("Toutes les catégories")
        categories = self.get_categories()
        categories.insert(0, "Toutes les catégories")
        category_dropdown = tk.OptionMenu(self.root, self.category_var, *categories, command=self.filter_products_by_category)
        category_dropdown.pack(pady=10)

    def show_products(self):
        # Supprimer les anciennes entrées
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Récupérer les produits depuis la base de données
        query = "SELECT product.id, product.name, product.description, product.price, product.quantity, category.name " \
                "FROM product INNER JOIN category ON product.id_category = category.id"
        cursor = self.db.connection.cursor()
        cursor.execute(query)
        products = cursor.fetchall()

        # Afficher les produits dans le Treeview
        for product in products:
            self.tree.insert('', 'end', values=product)

    def add_product(self):
        # Fenêtre popup pour saisir les détails du produit
        add_product_window = tk.Toplevel(self.root)
        add_product_window.title("Ajouter un produit")

        # Widgets pour saisir les détails du produit
        name_label = tk.Label(add_product_window, text="Nom du produit:")
        name_label.grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(add_product_window)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        description_label = tk.Label(add_product_window, text="Description:")
        description_label.grid(row=1, column=0, padx=10, pady=5)
        description_entry = tk.Entry(add_product_window)
        description_entry.grid(row=1, column=1, padx=10, pady=5)

        price_label = tk.Label(add_product_window, text="Prix:")
        price_label.grid(row=2, column=0, padx=10, pady=5)
        price_entry = tk.Entry(add_product_window)
        price_entry.grid(row=2, column=1, padx=10, pady=5)

        quantity_label = tk.Label(add_product_window, text="Quantité:")
        quantity_label.grid(row=3, column=0, padx=10, pady=5)
        quantity_entry = tk.Entry(add_product_window)
        quantity_entry.grid(row=3, column=1, padx=10, pady=5)

        category_label = tk.Label(add_product_window, text="Catégorie:")
        category_label.grid(row=4, column=0, padx=10, pady=5)

        # Obtenez les catégories de la base de données pour le menu déroulant
        categories = self.get_categories()

        category_var = tk.StringVar(add_product_window)
        category_var.set(categories[0])  # Définir la première catégorie par défaut

        category_dropdown = tk.OptionMenu(add_product_window, category_var, *categories)
        category_dropdown.grid(row=4, column=1, padx=10, pady=5)

        # Bouton pour ajouter le produit
        add_button = tk.Button(add_product_window, text="Ajouter", command=lambda: self.insert_product(
            name_entry.get(),
            description_entry.get(),
            price_entry.get(),
            quantity_entry.get(),
            category_var.get()
        ))
        add_button.grid(row=5, column=0, columnspan=2, pady=10)

    def insert_product(self, name, description, price, quantity, category):
        try:
            cursor = self.db.connection.cursor()

            # Récupérer l'ID de la catégorie sélectionnée
            cursor.execute("SELECT id FROM category WHERE name = %s", (category,))
            category_id = cursor.fetchone()[0]

            # Insérer le nouveau produit dans la base de données
            insert_query = "INSERT INTO product (name, description, price, quantity, id_category) VALUES (%s, %s, %s, %s, %s)"
            data = (name, description, price, quantity, category_id)
            cursor.execute(insert_query, data)

            # Commit et mise à jour de l'affichage des produits
            self.db.connection.commit()
            self.show_products()

            print("Produit ajouté avec succès.")
        except Error as e:
            print("Error adding product:", e)

    def remove_product(self):
        # Récupérer l'élément sélectionné dans le Treeview
        selected_item = self.tree.selection()

        if not selected_item:
            print("Aucun produit sélectionné.")
            return

        try:
            # Demander confirmation pour la suppression
            confirmation = tk.messagebox.askyesno("Supprimer le produit", "Êtes-vous sûr de vouloir supprimer ce produit?")
            if not confirmation:
                return

            # Récupérer l'ID du produit sélectionné
            product_id = self.tree.item(selected_item)['values'][0]

            # Exécuter la requête SQL pour supprimer le produit de la base de données
            delete_query = "DELETE FROM product WHERE id = %s"
            cursor = self.db.connection.cursor()
            cursor.execute(delete_query, (product_id,))

            # Commit et mise à jour de l'affichage des produits
            self.db.connection.commit()
            self.show_products()

            print("Produit supprimé avec succès.")
        except Error as e:
            print("Error removing product:", e)
            
    def update_product(self):
        # Récupérer l'élément sélectionné dans le Treeview
        selected_item = self.tree.selection()

        if not selected_item:
            print("Aucun produit sélectionné.")
            return

        # Récupérer les valeurs du produit sélectionné
        product_values = self.tree.item(selected_item)['values']

        # Fenêtre popup pour mettre à jour les informations du produit
        update_product_window = tk.Toplevel(self.root)
        update_product_window.title("Modifier le produit")

        # Widgets pour mettre à jour les informations du produit
        name_label = tk.Label(update_product_window, text="Nom du produit:")
        name_label.grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(update_product_window)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, product_values[1])  # Pré-remplir le champ avec le nom actuel

        description_label = tk.Label(update_product_window, text="Description:")
        description_label.grid(row=1, column=0, padx=10, pady=5)
        description_entry = tk.Entry(update_product_window)
        description_entry.grid(row=1, column=1, padx=10, pady=5)
        description_entry.insert(0, product_values[2])  # Pré-remplir le champ avec la description actuelle

        price_label = tk.Label(update_product_window, text="Prix:")
        price_label.grid(row=2, column=0, padx=10, pady=5)
        price_entry = tk.Entry(update_product_window)
        price_entry.grid(row=2, column=1, padx=10, pady=5)
        price_entry.insert(0, product_values[3])  # Pré-remplir le champ avec le prix actuel

        quantity_label = tk.Label(update_product_window, text="Quantité:")
        quantity_label.grid(row=3, column=0, padx=10, pady=5)
        quantity_entry = tk.Entry(update_product_window)
        quantity_entry.grid(row=3, column=1, padx=10, pady=5)
        quantity_entry.insert(0, product_values[4])  # Pré-remplir le champ avec la quantité actuelle

        # Bouton pour mettre à jour le produit
        update_button = tk.Button(update_product_window, text="Mettre à jour", command=lambda: self.perform_update(selected_item, name_entry.get(), description_entry.get(), price_entry.get(), quantity_entry.get()))
        update_button.grid(row=4, column=0, columnspan=2, pady=10)

    def perform_update(self, selected_item, name, description, price, quantity):
        try:
            # Récupérer l'ID du produit sélectionné
            product_id = selected_item[0]

            # Afficher les valeurs avant conversion
            print("Before conversion - Name:", name, "Description:", description, "Price:", price, "Quantity:", quantity)

            # Convertir les valeurs en types appropriés
            name = str(name)  # Assurez-vous que le nom est une chaîne de caractères
            description = str(description)  # Assurez-vous que la description est une chaîne de caractères
            price = float(price)  # Convertir le prix en nombre réel
            quantity = int(quantity)  # Convertir la quantité en nombre entier

            # Afficher les valeurs après conversion
            print("After conversion - Name:", name, "Description:", description, "Price:", price, "Quantity:", quantity)

            # Exécuter la requête SQL pour mettre à jour le produit dans la base de données
            print("Before SQL execution - Name:", name, "Description:", description, "Price:", price, "Quantity:", quantity, "Product ID:", product_id)
            update_query = "UPDATE product SET name=%s, description=%s, price=%s, quantity=%s WHERE id=%s"
            cursor = self.db.connection.cursor()
            cursor.execute(update_query, (name, description, price, quantity, product_id))
            self.db.connection.commit()

            # Mettre à jour l'affichage des produits
            self.show_products()

            print("Produit mis à jour avec succès.")
        except Error as e:
            print("Error updating product:", e)


    def export_csv(self):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM product INNER JOIN category ON product.id_category = category.id")
            products = cursor.fetchall()

            with open("products_export.csv", "w", newline='') as csvfile:
                csv_writer = csv.writer(csvfile)

                # Écrire l'en-tête du fichier CSV
                csv_writer.writerow(['ID', 'Nom', 'Description', 'Prix', 'Quantité', 'Catégorie'])

                # Écrire les données des produits dans le fichier CSV
                for product in products:
                    csv_writer.writerow(product)

            print("Export CSV réussi.")
        except Error as e:
            print("Error exporting CSV:", e)

    def get_categories(self):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT name FROM category")
            categories = [row[0] for row in cursor.fetchall()]
            return categories
        except Error as e:
            print("Error fetching categories:", e)
            return []
        
    def manage_categories(self):
        # Fenêtre popup pour gérer les catégories
        manage_categories_window = tk.Toplevel(self.root)
        manage_categories_window.title("Gérer les catégories")

        # Listebox pour afficher les catégories actuelles
        categories_listbox = tk.Listbox(manage_categories_window, selectmode=tk.SINGLE, height=5)
        categories_listbox.grid(row=0, column=0, padx=10, pady=10)

        # Boutons pour ajouter et supprimer des catégories
        add_button = tk.Button(manage_categories_window, text="Ajouter", command=self.add_category)
        add_button.grid(row=1, column=0, padx=10, pady=5)

        remove_button = tk.Button(manage_categories_window, text="Supprimer", command=lambda: self.remove_category(categories_listbox))
        remove_button.grid(row=2, column=0, padx=10, pady=5)

        # Afficher les catégories actuelles dans la Listbox
        current_categories = self.get_categories()
        for category in current_categories:
            categories_listbox.insert(tk.END, category)

    def add_category(self):
        # Fenêtre de dialogue pour saisir une nouvelle catégorie
        new_category = tkinter.simpledialog.askstring("Ajouter une catégorie", "Nom de la nouvelle catégorie:")

        if new_category:
            try:
                # Insérer la nouvelle catégorie dans la base de données
                insert_query = "INSERT INTO category (name) VALUES (%s)"
                cursor = self.db.connection.cursor()
                cursor.execute(insert_query, (new_category,))
                self.connection.commit()

                # Mettre à jour la Listbox avec les nouvelles catégories
                self.manage_categories()
                print("Nouvelle catégorie ajoutée avec succès.")
            except Error as e:
                print("Error adding category:", e)

    def remove_category(self, listbox):
        # Récupérer la catégorie sélectionnée dans la Listbox
        selected_category = listbox.get(listbox.curselection())

        if not selected_category:
            print("Aucune catégorie sélectionnée.")
            return

        try:
            # Demander confirmation pour la suppression
            confirmation = tk.messagebox.askyesno("Supprimer la catégorie", f"Êtes-vous sûr de vouloir supprimer la catégorie '{selected_category}'?")
            if not confirmation:
                return

            # Exécuter la requête SQL pour supprimer la catégorie de la base de données
            delete_query = "DELETE FROM category WHERE name = %s"
            cursor = self.db.connection.cursor()
            cursor.execute(delete_query, (selected_category,))
            self.connection.commit()

            # Mettre à jour la Listbox avec les catégories restantes
            self.manage_categories()
            print("Catégorie supprimée avec succès.")
        except Error as e:
            print("Error removing category:", e)

    def filter_products_by_category(self, event):
        selected_category = self.category_var.get()

        try:
            cursor = self.db.connection.cursor()

            if selected_category == "Toutes les catégories":
                # Si "Toutes les catégories" est sélectionné, afficher tous les produits
                cursor.execute("SELECT * FROM product INNER JOIN category ON product.id_category = category.id")
            else:
                # Sinon, filtrer les produits par catégorie sélectionnée
                cursor.execute("SELECT * FROM product INNER JOIN category ON product.id_category = category.id WHERE category.name = %s", (selected_category,))

            products = cursor.fetchall()

            # Effacer les anciennes entrées dans le Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Afficher les produits filtrés dans le Treeview
            for product in products:
                self.tree.insert('', 'end', values=product)

        except Error as e:
            print("Error filtering products by category:", e)

if __name__ == "__main__":
    root = tk.Tk()
    app = StockManagementApp(root)
    root.mainloop()