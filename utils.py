from itertools import islice

###### Get the version major number from release tag ######
def get_version_major(version):
    v_major = None
    parsed_chars = ""
    is_accepted = False
    for char in version:
        try:
            if v_major != None and isinstance(int(v_major), int) and char == ".":
                v_major = int(v_major)
                break
            temp = int(char)
            if parsed_chars == "" or ("v" in parsed_chars and parsed_chars[-1] == "v") or "version" in parsed_chars:
                is_accepted = True
                if v_major == None:
                    v_major = char
                else:
                    v_major += char.lower()
        except:
            parsed_chars += char
            pass
    
    if is_accepted == False:
        v_major = version
        
    return v_major

###### Get the first n key-value pairs from dictionary ######
def take(n, iterable):
    return list(islice(iterable, n))

###### Get the next key in dictionary ######
def get_next_key(current_key, iterable):
    keyList = list(iterable)
    for idx, key in enumerate(keyList):
        if key == current_key:
            next_key = None
            try:
                next_key = keyList[idx+1]            
            except:
                pass
            return next_key
        