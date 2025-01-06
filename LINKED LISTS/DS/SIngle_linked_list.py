# Node class to represent each node in the Linked List
class Node:
    def __init__(self, data):
        self.data = data  # Store data
        self.next = None  # Initialize next to None (by default)

# Linked List class
class LinkedList:
    def __init__(self):
        self.head = None  # Initialize the list with no nodes (empty list)
    
    # Method to insert a new node at the beginning
    def insert_at_beginning(self, data):
        new_node = Node(data)  # Create a new node
        new_node.next = self.head  # Point the new node to the current head
        self.head = new_node  # Make the new node the head of the list
    
    # Method to insert a new node at the end
    def insert_at_end(self, data):
        new_node = Node(data)  # Create a new node
        if self.head is None:  # If the list is empty, the new node becomes the head
            self.head = new_node
            return
        last = self.head
        while last.next:  # Traverse the list to find the last node
            last = last.next
        last.next = new_node  # Make the last node point to the new node
    
    # Method to insert a node at a specific position
    def insert_at_position(self, data, position):
        if position < 0:
            print("Position must be a non-negative integer.")
            return
        new_node = Node(data)
        current = self.head
        if position == 0:  # If the position is at the beginning
            new_node.next = self.head
            self.head = new_node
            return
        # Traverse the list to find the node just before the specified position
        for _ in range(position - 1):
            if current is None:
                print("Position is out of bounds.")
                return
            current = current.next
        new_node.next = current.next  # Point new node to the next of the current node
        current.next = new_node  # Point the current node to the new node
    
    # Method to delete a node from the beginning
    def delete_from_beginning(self):
        if self.head is None:
            print("The list is empty.")
            return
        self.head = self.head.next  # Make the head point to the next node
    
    # Method to delete a node from the end
    def delete_from_end(self):
        if self.head is None:
            print("The list is empty.")
            return
        if self.head.next is None:  # If only one node exists
            self.head = None
            return
        second_last = self.head
        while second_last.next and second_last.next.next:  # Traverse to the second last node
            second_last = second_last.next
        second_last.next = None  # Remove the last node
    
    # Method to print the entire list (traversal)
    def print_list(self):
        current = self.head
        if current is None:
            print("The list is empty.")
            return
        while current:
            print(current.data, end=" -> ")
            current = current.next
        print("None")

    # Method to search for an element in the list
    def search(self, key):
        current = self.head
        position = 0
        while current:
            if current.data == key:
                print(f"Element {key} found at position {position}")
                return
            position += 1
            current = current.next
        print(f"Element {key} not found in the list.")
    
    # Method to reverse the list
    def reverse(self):
        prev = None
        current = self.head
        while current:
            next_node = current.next  # Save the next node
            current.next = prev  # Reverse the link
            prev = current  # Move prev and current one step ahead
            current = next_node
        self.head = prev  # Make the last node as the new head

# Example usage
if __name__ == "__main__":
    linked_list = LinkedList()
    
    # Inserting nodes
    linked_list.insert_at_beginning(10)
    linked_list.insert_at_end(20)
    linked_list.insert_at_end(30)
    linked_list.insert_at_position(15, 1)
    
    print("Linked List after insertions:")
    linked_list.print_list()
    
    # Deleting nodes
    linked_list.delete_from_beginning()
    print("\nLinked List after deleting from beginning:")
    linked_list.print_list()
    
    linked_list.delete_from_end()
    print("\nLinked List after deleting from end:")
    linked_list.print_list()
    
    # Searching for an element
    linked_list.search(20)
    linked_list.search(40)
    
    # Reversing the list
    linked_list.reverse()
    print("\nLinked List after reversing:")
    linked_list.print_list()
