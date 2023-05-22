import pytest

from src.auraboros.ui import UIElement

def test_integration(self):
    element1 = UIElement()

# class TestMenuInterface:
#     def test_do_selected_action(self):
#         menuinterface = MenuInterface()
#         menuinterface.add_menuitem("test1", lambda: "return value")
#         assert menuinterface.do_selected_action() == "return value"

#     def test_cursor_down(self):
#         menuinterface = MenuInterface()
#         menuinterface.add_menuitem("test1")
#         menuinterface.add_menuitem("test2", lambda: "return value")
#         menuinterface.cursor_down()
#         assert menuinterface.selected_index == 1
#         assert menuinterface.do_selected_action() == "return value"

#     def test_cursor_up(self):
#         menuinterface = MenuInterface()
#         menuinterface.add_menuitem("test1")
#         menuinterface.add_menuitem("test2")
#         menuinterface.add_menuitem("test3", lambda: "return value")
#         menuinterface.cursor_up()
#         assert menuinterface.selected_index == 2
#         assert menuinterface.do_selected_action() == "return value"

#     def test_replace_menuitem_by_index(self):
#         menuinterface = MenuInterface()
#         menuinterface.add_menuitem("test1")
#         menuinterface.add_menuitem("test2")
#         menuinterface.replace_menuitem_by_index(1, "replaced")
#         assert menuinterface.option_keys[1] == "replaced"
#         assert menuinterface.option_texts[1] == "replaced"

#     def test_replace_menuitem_by_key(self):
#         menuinterface = MenuInterface()
#         menuinterface.add_menuitem("test1")
#         menuinterface.add_menuitem("test2")
#         menuinterface.replace_menuitem_by_key("test2", "replaced test2", text="new")
#         assert menuinterface.option_keys[1] == "replaced test2"
#         assert menuinterface.option_texts[1] == "new"

#     def test_do_action_when_menu_is_empty(self):
#         menuinterface = MenuInterface()
#         with pytest.raises(AttributeError):
#             menuinterface.do_selected_action()

#     def test_add_menuitem(self):
#         menuinterface = MenuInterface()
#         menuinterface.add_menuitem("test1")
#         assert menuinterface.option_keys == ["test1"]
#         assert menuinterface.option_texts == ["test1"]
