import time

class Room:
    def __init__(self, id_room):
        self.id_room = id_room

class BPTreeNode:
    def __init__(self, is_leaf=False):
        self.keys = []
        self.children = []
        self.is_leaf = is_leaf
        self.next = None  

class BPTree:
    def __init__(self, t=4):  
        self.root = BPTreeNode(is_leaf=True)
        self.t = t  
        self.count_room_no_empty = 0 
        
    def reset_tree(self):
        self.root = BPTreeNode(is_leaf=True)  
        self.count_room_no_empty = 0  
        print("Tree has been reset.")


    def search(self, key, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i].id_room:
            i += 1
        if node.is_leaf:
            if i < len(node.keys) and key == node.keys[i].id_room:
                print(f"Room {key} found at RAM address: {id(node)}")
                return node
            else:
                print(f"Room {key} not found")
                print()
                return None
        else:
            return self.search(key, node.children[i])
        
    def search_no_empty(self, key, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i].id_room:
            i += 1
        if node.is_leaf:
            if i < len(node.keys) and key == node.keys[i].id_room:
                return True
            else:
                return None
        else:
            return self.search_no_empty(key, node.children[i])

    def insert(self, room):
        root = self.root
        # if self.search_no_empty(room.id_room) is True:
        #     print(f"Room {room.id_room} already exists, skipping insertion.")
        #     return
        if len(root.keys) == (2 * self.t) - 1:
            new_node = BPTreeNode()
            self.root = new_node
            new_node.children.append(root)
            self.split_child(new_node, 0, root)
            self.insert_non_full(new_node, room)
        else:
            self.insert_non_full(root, room)

    def insert_non_full(self, node, room):
        i = len(node.keys) - 1
        if node.is_leaf:
            node.keys.append(None)  
            while i >= 0 and room.id_room < node.keys[i].id_room:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = room  
            self.count_room_no_empty += 1
            print(f"Room {room.id_room} added at node with RAM address: {id(node)}")
        else:
            while i >= 0 and room.id_room < node.keys[i].id_room:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.t) - 1:
                self.split_child(node, i, node.children[i])
                if room.id_room > node.keys[i].id_room:
                    i += 1
            self.insert_non_full(node.children[i], room)

    def split_child(self, parent, i, child):
        t = self.t
        new_node = BPTreeNode(is_leaf=child.is_leaf)
        parent.children.insert(i + 1, new_node)
        parent.keys.insert(i, child.keys[t - 1])

        new_node.keys = child.keys[t:(2 * t - 1)]
        child.keys = child.keys[0:(t - 1)]

        if not child.is_leaf:
            new_node.children = child.children[t:(2 * t)]
            child.children = child.children[0:t]
        else:
            new_node.next = child.next
            child.next = new_node

    def traverse(self, node=None):
        if node is None:
            node = self.root
        if node.is_leaf:
            for room in node.keys:
                print(f"Room {room.id_room} (RAM: {id(node)})")
        else:
            for i in range(len(node.keys)):
                self.traverse(node.children[i])
                print(f"Room {node.keys[i].id_room} (RAM: {id(node)})")
            self.traverse(node.children[len(node.keys)])

    def list_empty_rooms(self, max_room):
        """List all empty rooms."""
        occupied_rooms = self.get_all_keys()
        empty_rooms = [room for room in range(1, max_room + 1) if room not in occupied_rooms]
        print(f"\nAll empty rooms: {empty_rooms}")

    def get_all_keys(self):
        """Get all room ids from the B+ Tree."""
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
        keys = []
        while node:
            keys.extend([room.id_room for room in node.keys])
            node = node.next
        return keys

    def write_to_file(self, filename="hotel_data.txt"):
        """Write room ids and RAM positions to a file."""
        with open(filename, 'w') as file:
            node = self.root
            while not node.is_leaf:
                node = node.children[0]
            while node:
                for room in node.keys:
                    file.write(f"Room: {room.id_room}, RAM Position: {id(node)}\n")
                node = node.next
        print(f"Data written to file {filename}")
        
        
    def find_last_room(self):
        node = self.root
        while not node.is_leaf:
            node = node.children[-1]  

        if node.keys:
            last_room = node.keys[-1] 
            return last_room
        else:
            return None
        
    def find_amount_empty_room(self):
        last_room = self.find_last_room()
        if last_room is None :
            return 0
        return last_room.id_room - self.count_room_no_empty
    
    def search_by_id_room(self, id_room):
        if id_room > self.find_last_room().id_room :
            return "-----------> Not Found <------------ "
        else:
            room = self.search(id_room)
            if room is None :
                return "-----------> Empty room (ห้องว่าง)<------------ "
            else :
                return f"-------> Found (มีคนเข้าอยู่) , room_address = {id(room)} <------- "
            
    def delete(self, id_room):
        """Delete a room by its id_room."""
        node, parent, index = self.find_node_to_delete(id_room)
        if node is None:
            print(f"-------> Room {id_room} not found. <------- ")
            return

 
        print(f"-----------> Delete successfully <------------ ")
        del node.keys[index]
        self.count_room_no_empty -= 1


        if len(node.keys) < self.t - 1:
            self.fix_underflow(node, parent)

    def find_node_to_delete(self, id_room, node=None, parent=None):
        """Find the node and its parent where the room with id_room is located."""
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and id_room > node.keys[i].id_room:
            i += 1
        if node.is_leaf:
            if i < len(node.keys) and id_room == node.keys[i].id_room:
                return node, parent, i
            else:
                return None, None, None
        else:
            return self.find_node_to_delete(id_room, node.children[i], node)

    def fix_underflow(self, node, parent):
        """Fix underflow in B+ Tree when a node has too few keys."""
        if parent is None:
            # Root case
            if len(self.root.keys) == 0 and not self.root.is_leaf:
                self.root = self.root.children[0]  # Promote child as root
            return

        idx = parent.children.index(node)
        left_sibling = parent.children[idx - 1] if idx > 0 else None
        right_sibling = parent.children[idx + 1] if idx < len(parent.children) - 1 else None

        if left_sibling and len(left_sibling.keys) > self.t - 1:
            # Borrow from left sibling
            node.keys.insert(0, parent.keys[idx - 1])
            parent.keys[idx - 1] = left_sibling.keys.pop()
        elif right_sibling and len(right_sibling.keys) > self.t - 1:
            # Borrow from right sibling
            node.keys.append(parent.keys[idx])
            parent.keys[idx] = right_sibling.keys.pop(0)
        else:
            # Merge with sibling
            if left_sibling:
                left_sibling.keys.extend(node.keys)
                parent.keys.pop(idx - 1)
                parent.children.pop(idx)
            else:
                node.keys.extend(right_sibling.keys)
                parent.keys.pop(idx)
                parent.children.pop(idx + 1)
                
    def write_to_file(self, filename="hotel_data.txt"):
        """Write room ids and RAM positions to a file."""
        with open(filename, 'w') as file:
            node = self.root
            while not node.is_leaf:
                node = node.children[0]
            while node:
                for room in node.keys:
                    file.write(f"Room: {room.id_room}, RAM Position: {id(node)} , {node}\n")
                node = node.next
        print(f"Data written to file {filename}")

    def add_data_by_amount(self, A, B, C, D,E):
        for a in range(1,A+1):
            for b in range(1,B+1):
                for c in range(1,C+1):
                    for d in range(1,D+1):
                        for e in range(1,E+1):
                            id_room = (2**a)*(3**b)*(5**c)*(7**d)*(11**e)
                            self.insert(Room(id_room))
                            
    def origin_of_room_number(self, id_room):
        a, b, c, d, e = 0, 0, 0, 0, 0
        while id_room % 2 == 0:
            id_room //= 2
            a += 1
        while id_room % 3 == 0:
            id_room //= 3
            b += 1
        while id_room % 5 == 0:
            id_room //= 5
            c += 1
        while id_room % 7 == 0:
            id_room //= 7
            d += 1
        while id_room % 11 == 0:
            id_room //= 11
            e += 1
        if id_room != 1:
            raise ValueError("id_room cannot be factored into the form 2^a * 3^b * 5^c * 7^d * 11^e")
        return a, b, c, d, e

def time_function(func, *args, **kwargs):
    start_time = time.time()  
    result = func(*args, **kwargs) 
    end_time = time.time() 
    execution_time = end_time - start_time
    return execution_time  




tree = BPTree()
while True:
    print("-------------- Start ------------------")
    print("Option ")
    print(" 1 : Add one room (เพิ่มทีละห้อง)")
    print(" 2 : Add more room (เพิ่มทีหลายห้อง)")
    print(" 3 : Delete room (ลบ)")
    print(" 4 : Find Total number of rooms inserted (หาจำนวนห้องทั้งหมดที่มีคนเข้าพักอยู่)")
    print(" 5 : Find Total empty rooms (หาจำนวนห้องว่างทั้งหมด)")
    print(" 6 : Search room by id (ค้นหาห้องโดย id_room)")
    print(" 7 : Search origin of room number  (ค้นหาหาช่องทางการเดินทางจาก id_room)")
    print(" 8 : Sava data to file (บันทึกข้อมูลห้องลงในไฟล์)")
    print(" exit : End program (ออก)")
    inp = input("Choose options : ")
    if inp == '1':
        print()
        print(" > Add one room (เพิ่มทีละห้อง)")
        print("Ex (id_room): 11111")
        id_room  = int(input("Input id room : "))
        if tree.search_no_empty(id_room) is None:
            times = time_function(tree.insert, Room(id_room))
            print()
            print(f"Time all : {times} seconds")
            print()
            print("----> Add room successfully <----")
            print()
        else:
            print(f"Room {id_room} already exists, skipping insertion.")
            print()
            print("----> Add room unsuccessfully <----")
            print()
        
    elif inp == '2':
        print()
        print(" > Add more room (เพิ่มทีหลายห้อง) (reset all)")
        print("ระบบจะล้างข้อมุลที่มีมาก่อนหน้าทั้งหมด")
        print("ใส่ช่องทางของห้องที่ต้องการเพิ่ม (ช่องทางที่ 1 ,ช่องทางที่ 2 ,ช่องทางที่ 3 ,ช่องทางที่ 4 ,ช่องทางที่ 5 ) ")
        print("Ex : 10,10,10,10,10 (จะได้ 100000 ห้อง)")
        A , B , C , D , E  = map(int , input("Input travel channel : ").split(","))
        tree.reset_tree()
        times = time_function(tree.add_data_by_amount, A, B, C, D, E)
        print()
        print(f"Time all : {times} seconds")
        print()
        print("---->Add room successfully <----")
        print()
    elif inp == '3' :
        print()
        print(" > Delete room (ลบ)")
        print("ใส่หมายเลขห้องที่ต้องการลบ (id_room)")
        print("Ex : 111111")
        id_room  = int(input("Input room id : "))
        print()
        times = time_function(tree.delete, id_room)
        print()
        print(f"Time all : {times} seconds")
        print()
    elif inp == '4' :
        print()
        print(" > Find Total number of rooms inserted (หาจำนวนห้องทั้งหมดที่มีคนเข้าพักอยู่)")
        print()
        print(f"Total number of rooms inserted : {tree.count_room_no_empty}")
        print()
    elif inp == '5' :
        print()
        print(" > Find Total empty rooms (หาจำนวนห้องว่างทั้งหมด)")
        print()
        print(f"Total empty rooms : {tree.find_amount_empty_room()}")
        print()
    elif inp == '6' :
        print()
        print(" > Search room by id (ค้นหาห้องโดย id_room)")
        print("ใส่หมายเลขห้องที่ต้องการค้นหา (id_room)")
        print("Ex : 111111")
        id_room  = int(input("Input room id : "))
        print()
        print(f"{tree.search_by_id_room(id_room)}")
        print()
    elif inp == '7' :
        print()
        print(" > Search origin of room number  (ค้นหาหาช่องทางการเดินทางจาก id_room)")
        print("ใส่หมายเลขห้องที่ต้องการค้นหาหาช่องทางการเดินทาง (id_room)")
        print("Ex : 111111")
        id_room  = int(input("Input room id : "))
        print()
        a, b, c, d, e = tree.origin_of_room_number(id_room)
        print(f"ช่องทางที่ 1 = {a}")
        print(f"ช่องทางที่ 2 = {b}")
        print(f"ช่องทางที่ 3 = {c}")
        print(f"ช่องทางที่ 4 = {d}")
        print(f"ช่องทางที่ 5 = {e}")
        print()
        print(f"----- a={a} b={b} c={d} d={e} e={e} ------")
        print()
    elif inp == '8' :
        print()
        print(" > Sava data to file (บันทึกข้อมูลห้องลงในไฟล์)")
        print("ใส่หมายเลขห้องที่ต้องการค้นหา (id_room)")
        print("Ex : hotel_data.txt")
        name_file = input("Input name file [name].txt : ")
        print()
        times = time_function(tree.write_to_file, name_file)
        print()
        print(f"Time all : {times} seconds")
        print()
        print("---->Sava data to file successfully <----")
        print()
    elif inp == 'exit' :
        break
    else :
        print()
        print("-------------- Eror -------------------")
        print()
        print(f"Choose agent !!!")

    print()
    
print("-------------- End All ------------------")



# Add rooms to the hotel
# time_function(tree.add_data_by_amount, 10, 10, 10, 10, 100)

# Traverse and print all rooms
# print("\nTraversing B+ Tree:")
# tree.traverse()

# Check rooms ที่มีคนอยู่
# print(f"\nTotal number of rooms inserted: {tree.count_room_no_empty}")

# Check rooms ที่ไม่มีคนอยู่
# print(f"\nTotal empty rooms : {tree.find_amount_empty_room()}");
# print()

# search 
# query_key = 3250436928818501593710000000000435345345
# print(f"\nSearching id={query_key} B+ Tree : {tree.search_by_id_room(query_key)}")

# delete by id_room
# delete_key = 393302868387038692838910000000000
# tree.delete(delete_key)

# search 
# query_key = 393302868387038692838910000000000
# print(f"\nSearching id={query_key} B+ Tree : {tree.search_by_id_room(query_key)}")

# เรียกใช้ฟังก์ชันเพื่อบันทึกข้อมูลห้องลงในไฟล์
# tree.write_to_file("hotel_rooms_data.txt")

# origin of room number 
# a, b, c, d, e = tree.origin_of_room_number(4326331552257425621228010000000000)
# print(f"a={a} b={b} c={d} d={e} e={e}")
