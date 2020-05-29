import sqlite3
import time

current_time = lambda: int(round(time.time() * 1000))

class Memory:
    def __init__(self, title, content, feeling, time, memory_id=None):
        self.title = title
        self.content = content
        self.time = time
        self.feeling = feeling
        self.id = memory_id

    def in_db(self):
        return self.id is not None

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DBProvider:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = dict_factory

        try:
            self.conn.execute('SELECT id FROM memories LIMIT 1')
        except:
            self._create_tables()

    def _create_tables(self):
        self.conn.execute('''
        CREATE TABLE memories (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          content TEXT NOT NULL,
          feeling TEXT NOT NULL,
          time INTEGER NOT NULL
        );
        ''')

    def commit(self):
        self.conn.commit()

    def execute(self, sql, values=[]):
        return self.conn.execute(sql, values)

    def execute_return_lastrowid(self, sql, values=[]):
        c = self.cursor()
        c.execute(sql, values)
        return c.lastrowid

    def cursor(self):
        return self.conn.cursor()

    def add_memory_row(self, title, content, feeling, time):
        return self.execute_return_lastrowid('INSERT INTO memories (title, content,\
                                              feeling, time) VALUES (?, ?, ?, ?)',
                                             (title, content, feeling, time))

    def add_memory(self, memory):
        mem_id = self.add_memory_row(memory.title, memory.content, memory.feeling,
                                     memory.time)
        memory.id = mem_id
        self.commit()

    def get_memories(self):
        mems = []
        for mem_row in self.execute('SELECT * FROM memories').fetchall():
            mems.append(Memory(mem_row['title'], mem_row['content'], mem_row['feeling'],
                               mem_row['time'], mem_row['id']))
        return mems

    def update_memory_row(self, memory_id, title, content, feeling, time):
        self.execute('UPDATE memories SET title = ?, content = ?, feeling = ?, time = ?\
                      WHERE id = ?', (title, content, feeling, time, memory_id))

    def update_memory(self, memory):
        self.update_memory_row(memory.id, memory.title, memory.content, memory.feeling,
                               memory.time)
        self.commit()

    def delete_memory_row(self, memory_id):
        self.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
        self.commit()

    def delete_memory(self, memory):
        self.delete_memory_row(memory.id)
