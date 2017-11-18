""" Test this module """
import unittest
from datetime import datetime
from . import Todo
from .todo import DATE_FORMAT

class TestTodoSorting(unittest.TestCase):
    """ Test Todo class sorting functionality """
    def test_sort_simple(self):
        todo1 = Todo("(A) 2017-11-17 ZZZ +foo1 @bar3 due:2017-11-18 t:2017-11-16")
        todo2 = Todo("(B) 2017-11-10 AAA +foo2 @bar1 due:2017-11-17 t:2017-11-15")
        todo3 = Todo("x (C) 2017-11-01 JJJ +foo3 @bar2 due:2017-11-19 t:2017-11-18")
        todo_list = [todo1, todo2, todo3]
        todo_list = Todo.sorted_todos(todo_list, keys=["completed"], reverses=[True])
        self.assertEqual(todo_list, [todo3, todo1, todo2])
        todo_list = Todo.sorted_todos(todo_list, keys=["priority"])
        self.assertEqual(todo_list, [todo1, todo2, todo3])
        todo_list = Todo.sorted_todos(todo_list, keys=["priority"], reverses=[True])
        self.assertEqual(todo_list, [todo3, todo2, todo1])
        todo_list = Todo.sorted_todos(todo_list, keys={"creation_date"})
        self.assertEqual(todo_list, [todo3, todo2, todo1])

    def test_sort_complex(self):
        todo1 = Todo("(A) 2017-11-10 ZZZ +foo1 @bar3 due:2017-11-18 t:2017-11-16")
        todo2 = Todo("(B) 2017-11-10 AAA +foo2 @bar1 due:2017-11-17 t:2017-11-15")
        todo3 = Todo("x (C) 2017-11-01 JJJ +foo3 @bar2 due:2017-11-19 t:2017-11-18")
        todo_list = [todo1, todo2, todo3]
        todo_list = Todo.sorted_todos(todo_list, keys=["description", "creation_date"])
        self.assertEqual(todo_list, [todo3, todo2, todo1])


class TestTodoParsing(unittest.TestCase):
    """ Test Todo class parsing functionality """
    def test_repr(self):
        todo1 = Todo("x (B) 2017-11-18 2017-11-17 Meh +foo +bar @baz due:2017-11-18 t:2017-11-17")
        todo2 = Todo(str(todo1))
        self.assertEqual(todo1, todo2)

    def test_eq(self):
        todo1 = Todo("x (B) 2017-11-18 2017-11-17 Meh +foo +bar @baz due:2017-11-18 t:2017-11-17")
        todo2 = Todo("x (B) 2017-11-18 2017-11-17 Meh +foo +bar @baz due:2017-11-18 t:2017-11-17")
        todo3 = Todo("(B) 2017-11-18 2017-11-17 Meh +foo +bar @baz due:2017-11-18 t:2017-11-17")
        self.assertEqual(todo1, todo2)
        self.assertNotEqual(todo1, todo3)

    def test_completed(self):
        todo = Todo()
        todo.parse_string("x This task is complete")
        self.assertTrue(todo.completed)
        todo.parse_string("This task is incomplete")
        self.assertFalse(todo.completed)

    def test_priority(self):
        todo = Todo("This task has no priority")
        self.assertIsNone(todo.priority)
        todo.parse_string("(A) This task has a priority")
        self.assertEqual(todo.priority, "A")
        todo.parse_string("x (X) This task has a priority")
        self.assertEqual(todo.priority, "X")

    def test_completion_date(self):
        todo = Todo("This task is incomplete")
        self.assertIsNone(todo.completion_date)
        todo.parse_string("x This task is complete but has no completion date")
        self.assertIsNone(todo.completion_date)
        todo.parse_string("x 17-11-10 This task is complete but has a mis-formatted completion date")
        self.assertIsNone(todo.completion_date)
        todo.parse_string("x 2017-11-10 This task is complete but is missing the creation date")
        self.assertIsNone(todo.completion_date)
        todo.parse_string("x 2017-11-10 2017-11-09 This task is complete")
        self.assertEqual(todo.completion_date, datetime.strptime("2017-11-10", DATE_FORMAT), todo.completion_date)
        self.assertEqual(todo.creation_date, datetime.strptime("2017-11-09", DATE_FORMAT), todo.creation_date)

    def test_creation_date(self):
        todo = Todo("This task has no creation date")
        self.assertIsNone(todo.creation_date)
        todo.parse_string("x 2017-11-10 This task is complete and has a creation date")
        self.assertEqual(todo.creation_date, datetime.strptime("2017-11-10", DATE_FORMAT), todo.creation_date)
        todo.parse_string("x 2017-11-10 2001-01-01 This task is complete and has a creation date")
        self.assertEqual(todo.completion_date, datetime.strptime("2017-11-10", DATE_FORMAT), todo.completion_date)
        self.assertEqual(todo.creation_date, datetime.strptime("2001-01-01", DATE_FORMAT), todo.creation_date)
        todo.parse_string("2017-11-10 This task is incomplete and has a creation date")
        self.assertEqual(todo.creation_date, datetime.strptime("2017-11-10", DATE_FORMAT), todo.creation_date)

    def test_metadata(self):
        todo = Todo("2017-11-17 This task has a due date due:2017-12-01")
        self.assertEqual(todo.due_date, datetime.strptime("2017-12-01", DATE_FORMAT))
        todo.parse_string("2017-11-17 This task has a start date t:2017-12-01")
        self.assertEqual(todo.start_date, datetime.strptime("2017-12-01", DATE_FORMAT))
        with self.assertRaises(AttributeError):
            todo.parse_string("2017-11-17 This task has bad metadata foo:bar")

    def test_description(self):
        todo = Todo("This task has no projects @bar")
        self.assertEqual(todo.projects, [])
        self.assertEqual(todo.contexts, ["bar"])
        self.assertEqual(todo.description, "This task has no projects")
        todo.parse_string("This task has no contexts +foo")
        self.assertEqual(todo.projects, ["foo"])
        self.assertEqual(todo.contexts, [])
        self.assertEqual(todo.description, "This task has no contexts")
        todo.parse_string("This task has contexts +foo and projects @bar +baz and some extra stuff")
        self.assertEqual(todo.projects, ["foo", "baz"])
        self.assertEqual(todo.contexts, ["bar"])
        self.assertEqual(todo.description, "This task has contexts and projects and some extra stuff")