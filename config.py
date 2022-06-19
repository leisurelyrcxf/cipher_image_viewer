def get_keys():
    from pathlib import Path
    home = Path.home()

    import os
    config_dir=os.path.join(home, ".config/cipher_viewer")
    if os.path.exists(os.path.join(config_dir, "keys")):
        D, N = load_keys(os.path.join(config_dir, "keys"))
    elif os.path.exists(os.path.join(config_dir, "default_keys")):
        D, N = load_keys(os.path.join(config_dir, "default_keys"))
    else:
        print("can't find decrypt keys config file")
        exit(1)
    print("D: %d, N: %d" % (D, N))
    return D, N

def load_keys(filename):
    with open(filename, "r") as fr:
        line = fr.readline()
        parts = line.split(" ")
        if not parts:
            print("invalid config file")
            exit(1)

        if len(parts) != 2:
            print("invalid config file")
            exit(1)

        D = int(parts[0].strip())
        N = int(parts[1].strip())
        if N > 256**3:
            print("N must be not greater than 256*256*256")
            exit(1)
        if N < 32*256:
            print("N must be not less than 32*256")
            exit(1)

        return D, N

