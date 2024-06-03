"""  Meta classes for abstract algebras

     MetaOp: meta class for operators Add, Mul, pow
     MetaElement: meta class for elements of the algebra


"""

class MetaOp(type):
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        if type(instance) == cls and "algebra" in kwargs:
            setattr(instance, 'algebra', 100)
            # setattr(instance, '_op_priority', 10)
        return instance


class MetaElement(type):
    """ Package the necessary attributes into the algebra attribute """
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        setattr(instance, 'algebra', 200)
        return instance
