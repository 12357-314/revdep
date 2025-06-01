class Parcel:
    def __init__(self, index_start, index_end, value, kind):
        self.index_start = index_start
        self.index_end = index_end
        self.value = value
        self.kind = kind

    def __repr__(self): return (
        f"{self.kind}: {self.value} "
        f"({self.index_start},{self.index_end})")


