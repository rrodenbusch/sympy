# MetaClass is to Class as Class is to Instance
# VectorSpace is a MetaClass
# InnerProductSpace is a MetaClass

class ExampleMetaClass(type):
    pass


class SubClass(metaclass=ExampleMetaClass):
    pass


subclass_object = SubClass()

if __name__ == "__main__":
    print(f"subclass_object's class is {subclass_object.__class__}/n")
    print(f"SubClass's class is {subclass_object.__class__.__class__}/n")
    print(f"ExampleMetaClass's class is {subclass_object.__class__.__class__.__class__}")
