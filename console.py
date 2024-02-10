import cmd
import re
import json
from models.base_model import BaseModel
from models import storage


class HBNBCommand(cmd.Cmd):

    prompt = "(hbnb) "

    def default(self, line):
        self._precmd(line)

    def _precmd(self, line):
        match = re.search(r"^(\w*)\.(\w+)(?:\(([^)]*)\))$", line)
        if not match:
            return line

        classname, method, args = match.groups()
        match_uid_and_args = re.search('^"([^"]*)"(?:, (.*))?$', args)
        uid, attr_or_dict = (match_uid_and_args.group(1), match_uid_and_args.group(2)) if match_uid_and_args else (args, False)

        attr_and_value = ""
        if method == "update" and attr_or_dict:
            match_dict = re.search('^({.*})$', attr_or_dict)
            if match_dict:
                self.update_dict(classname, uid, match_dict.group(1))
                return ""

            match_attr_and_value = re.search('^(?:"([^"]*)")?(?:, (.*))?$', attr_or_dict)
            if match_attr_and_value:
                attr_and_value = (match_attr_and_value.group(1) or "") + " " + (match_attr_and_value.group(2) or "")

        command = f"{method} {classname} {uid} {attr_and_value}"
        self.onecmd(command)
        return command

    def update_dict(self, classname, uid, s_dict):
        s = s_dict.replace("'", '"')
        d = json.loads(s)

        if not classname:
            print("** class name missing **")
        elif classname not in storage.classes():
            print("** class doesn't exist **")
        elif uid is None:
            print("** instance id missing **")
        else:
            key = f"{classname}.{uid}"
            if key not in storage.all():
                print("** no instance found **")
            else:
                attributes = storage.attributes()[classname]
                for attribute, value in d.items():
                    if attribute in attributes:
                        value = attributes[attribute](value)
                    setattr(storage.all()[key], attribute, value)
                storage.all()[key].save()

    def do_EOF(self, line):
        print()
        return True

    def do_quit(self, line):
        return True

    def emptyline(self):
        pass

    def do_create(self, line):
        if not line:
            print("** class name missing **")
        elif line not in storage.classes():
            print("** class doesn't exist **")
        else:
            obj = storage.classes()[line]()
            obj.save()
            print(obj.id)

    def do_show(self, line):
        if not line:
            print("** class name missing **")
        else:
            words = line.split()
            if words[0] not in storage.classes():
                print("** class doesn't exist **")
            elif len(words) < 2:
                print("** instance id missing **")
            else:
                key = f"{words[0]}.{words[1]}"
                if key not in storage.all():
                    print("** no instance found **")
                else:
                    print(storage.all()[key])

    def do_destroy(self, line):
        if not line:
            print("** class name missing **")
        else:
            words = line.split()
            if words[0] not in storage.classes():
                print("** class doesn't exist **")
            elif len(words) < 2:
                print("** instance id missing **")
            else:
                key = f"{words[0]}.{words[1]}"
                if key not in storage.all():
                    print("** no instance found **")
                else:
                    del storage.all()[key]
                    storage.save()

    def do_all(self, line):
        if line:
            words = line.split()
            if words[0] not in storage.classes():
                print("** class doesn't exist **")
            else:
                obj_list = [str(obj) for key, obj in storage.all().items() if type(obj).__name__ == words[0]]
                print(obj_list)
        else:
            obj_list = [str(obj) for key, obj in storage.all().items()]
            print(obj_list)

    def do_count(self, line):
        words = line.split()
        if not words[0]:
            print("** class name missing **")
        elif words[0] not in storage.classes():
            print("** class doesn't exist **")
        else:
            matches = [k for k in storage.all() if k.startswith(words[0] + '.')]
            print(len(matches))

    def do_update(self, line):
        if not line:
            print("** class name missing **")
            return

        rex = r'^(\S+)(?:\s(\S+)(?:\s(\S+)(?:\s((?:"[^"]*")|(?:(\S)+)))?)?)?'
        match = re.search(rex, line)
        classname, uid, attribute, value = match.groups() if match else (None, None, None, None)

        if not match:
            print("** class name missing **")
        elif classname not in storage.classes():
            print("** class doesn't exist **")
        elif uid is None:
            print("** instance id missing **")
        else:
            key = f"{classname}.{uid}"
            if key not in storage.all():
                print("** no instance found **")
            elif not attribute:
                print("** attribute name missing **")
            elif not value:
                print("** value missing **")
            else:
                cast = None
                if not re.search('^".*"$', value):
                    if '.' in value:
                        cast = float
                    else:
                        cast = int
                else:
                    value = value.replace('"', '')

                attributes = storage.attributes()[classname]
                if attribute in attributes:
                    value = attributes[attribute](value)

                elif cast:
                    try:
                        value = cast(value)
                    except ValueError:
                        pass

                setattr(storage.all()[key], attribute, value)
                storage.all()[key].save()


if __name__ == '__main__':
    HBNBCommand().cmdloop()

