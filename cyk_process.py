import grammar

def create_table(n):
    """
    Membuat tabel kosong berukuran n x n.
    Setiap sel berisi set() kosong untuk menyimpan Non-Terminal.
    
    Args:
        n (int): Ukuran tabel (jumlah kata dalam kalimat)
        
    Returns:
        list: Tabel 2D berisi set() kosong
    """
    return [[set() for _ in range(n)] for _ in range(n)]

def create_backpointer_table(n):
    """
    Membuat tabel backpointer untuk menyimpan informasi derivasi.
    Setiap sel berisi dictionary: {non_terminal: (split_point, left_NT, right_NT)}
    
    Args:
        n (int): Ukuran tabel
        
    Returns:
        list: Tabel 2D berisi dictionary kosong
    """
    return [[{} for _ in range(n)] for _ in range(n)]

def get_combinations(set_a, set_b):
    """
    Menggabungkan dua set string untuk simulasi aturan CNF: A -> B C.
    Jika set_a = {'P'} dan set_b = {'S'}, hasilnya ['PS'].
    
    Args:
        set_a (set): Set pertama (dari sel kiri dalam tabel CYK)
        set_b (set): Set kedua (dari sel kanan dalam tabel CYK)
        
    Returns:
        list: List gabungan string dari kedua set
    """
    results = []
    if not set_a or not set_b:
        return results
    
    for a in set_a:
        for b in set_b:
            results.append(a + b)
    return results

def cyk_parse(words):
    """
    Implementasi Algoritma Cocke-Younger-Kasami (CYK) untuk parsing kalimat.
    Menggunakan bottom-up triangular table (X[i,j] dimana i adalah row dari bawah)
    
    Algoritma ini bekerja dalam dua tahap:
    1. Pengisian baris bawah (length=1): Mengisi berdasarkan aturan terminal
    2. Pengisian ke atas (length 2-n): Mengisi berdasarkan aturan branching
    
    Args:
        words (list): List kata yang sudah divalidasi
        
    Returns:
        tuple: (table, backpointer) - Tabel CYK dan backpointer untuk trace
    """
    n = len(words)
    
    table = create_table(n)
    backpointer = create_backpointer_table(n)
    
    for col in range(n):
        word = words[col]
        produces = grammar.check_production([word])
        
        if produces:
            table[0][col] = set(produces)
            for nt in produces:
                backpointer[0][col][nt] = ('terminal', word, col)

    for length in range(2, n + 1):
        row = length - 1
        
        for col in range(n - length + 1):
            for k in range(1, length):
                left_row = k - 1
                left_col = col
                
                right_row = length - k - 1
                right_col = col + k
                
                left_cell = table[left_row][left_col]
                right_cell = table[right_row][right_col]
                
                combinations = get_combinations(left_cell, right_cell)
                
                if combinations:
                    valid_parents = grammar.check_production(combinations)
                    if valid_parents:
                        table[row][col].update(valid_parents)
                        
                        for parent in valid_parents:
                            for combo in combinations:
                                if combo in grammar.production.get(parent, []):
                                    backpointer[row][col][parent] = (
                                        k, combo, left_row, left_col, right_row, right_col
                                    )
                                    break

    return table, backpointer

def is_valid_sentence(table, n, start_symbol="K"):
    """
    Mengecek apakah kalimat valid berdasarkan tabel CYK hasil parsing.
    Untuk bottom-up table: hasil akhir ada di baris paling atas (row n-1, col 0)
    
    Args:
        table (list): Tabel CYK yang sudah terisi (bisa tuple dari cyk_parse)
        n (int): Panjang kalimat (jumlah kata)
        start_symbol (str): Simbol awal grammar (default: "K")
        
    Returns:
        bool: True jika kalimat valid, False jika tidak
    """
    if isinstance(table, tuple):
        table = table[0]
    
    top_cell = table[n-1][0]
    return start_symbol in top_cell

def get_parse_result(table, n):
    """
    Mendapatkan hasil parsing dari sel terakhir tabel CYK.
    Untuk bottom-up table: hasil ada di row n-1, col 0
    
    Args:
        table (list): Tabel CYK yang sudah terisi
        n (int): Panjang kalimat
        
    Returns:
        set: Set non-terminal di sel paling atas
    """
    return table[n-1][0]

def build_parse_tree(non_terminal, row, col, backpointer, words):
    """
    Membangun parse tree secara rekursif dari backpointer.
    Menggunakan bottom-up indexing (row=level, col=start position)
    
    Args:
        non_terminal (str): Non-terminal yang akan di-trace
        row (int): Baris dalam tabel (0=bottom, n-1=top)
        col (int): Kolom (posisi kata awal)
        backpointer (list): Tabel backpointer
        words (list): List kata asli
        
    Returns:
        dict: Parse tree dalam bentuk nested dictionary
    """
    n = len(words)
    
    if row < 0 or row >= n or col < 0 or col >= n:
        return None
    
    if non_terminal not in backpointer[row][col]:
        return None
    
    pointer = backpointer[row][col][non_terminal]
    
    length = row + 1
    start_idx = col
    end_idx = col + length - 1
    
    if pointer[0] == 'terminal':
        word = pointer[1]
        word_index = pointer[2]
        return {
            'label': non_terminal,
            'type': 'terminal',
            'word': word,
            'position': word_index,
            'span': (start_idx, end_idx)
        }
    
    k, combo, left_row, left_col, right_row, right_col = pointer
    
    left_candidates = backpointer[left_row][left_col]
    right_candidates = backpointer[right_row][right_col]
    
    left_nt = None
    right_nt = None
    
    for left in left_candidates:
        for right in right_candidates:
            if left + right == combo:
                left_nt = left
                right_nt = right
                break
        if left_nt and right_nt:
            break
    
    if not left_nt or not right_nt:
        return {
            'label': non_terminal,
            'type': 'non-terminal',
            'production': combo,
            'span': (start_idx, end_idx)
        }
    
    return {
        'label': non_terminal,
        'type': 'non-terminal',
        'production': f"{non_terminal} → {left_nt} {right_nt}",
        'span': (start_idx, end_idx),
        'left': build_parse_tree(left_nt, left_row, left_col, backpointer, words),
        'right': build_parse_tree(right_nt, right_row, right_col, backpointer, words)
    }

def get_sentence_pattern(backpointer, words, start_symbol="K"):
    """
    Mendapatkan pola kalimat dari hasil parsing.
    Untuk bottom-up table: start dari row n-1, col 0
    
    Args:
        backpointer (list): Tabel backpointer
        words (list): List kata
        start_symbol (str): Start symbol grammar
        
    Returns:
        dict: Informasi pola kalimat
    """
    n = len(words)
    
    if start_symbol not in backpointer[n-1][0]:
        return None
    
    parse_tree = build_parse_tree(start_symbol, n-1, 0, backpointer, words)
    
    pattern = extract_pattern(parse_tree)
    
    return {
        'parse_tree': parse_tree,
        'pattern': pattern,
        'derivation': get_derivation_steps(parse_tree)
    }

def extract_pattern(node, depth=0):
    """
    Ekstrak pola dari parse tree secara rekursif.
    
    Args:
        node (dict): Node dari parse tree
        depth (int): Kedalaman node
        
    Returns:
        str: Representasi pola
    """
    if node is None:
        return ""
    
    if node['type'] == 'terminal':
        return f"{node['label']}"
    
    left_pattern = extract_pattern(node.get('left'), depth + 1)
    right_pattern = extract_pattern(node.get('right'), depth + 1)
    
    if depth == 0:
        return f"{node['label']} → {left_pattern} {right_pattern}"
    
    return f"{node['label']}"

def get_derivation_steps(node, depth=0):
    """
    Mendapatkan langkah-langkah derivasi dari parse tree.
    
    Args:
        node (dict): Node dari parse tree
        depth (int): Kedalaman saat ini
        
    Returns:
        list: List langkah derivasi
    """
    if node is None:
        return []
    
    steps = []
    
    if node['type'] == 'non-terminal' and 'production' in node:
        steps.append({
            'depth': depth,
            'rule': node['production'],
            'span': node['span']
        })
        
        if 'left' in node:
            steps.extend(get_derivation_steps(node['left'], depth + 1))
        if 'right' in node:
            steps.extend(get_derivation_steps(node['right'], depth + 1))
    
    return steps

def format_parse_tree(node, words, indent=0, prefix=""):
    """
    Format parse tree menjadi string yang mudah dibaca.
    
    Args:
        node (dict): Node dari parse tree
        words (list): List kata
        indent (int): Level indentasi
        prefix (str): Prefix untuk garis tree
        
    Returns:
        str: Parse tree dalam format string
    """
    if node is None:
        return ""
    
    result = prefix + node['label']
    
    if node['type'] == 'terminal':
        result += f" → '{node['word']}'\n"
    else:
        result += "\n"
        
        if 'left' in node and node['left']:
            result += format_parse_tree(node['left'], words, indent + 1, prefix + "  ├─ ")
        
        if 'right' in node and node['right']:
            result += format_parse_tree(node['right'], words, indent + 1, prefix + "  └─ ")
    
    return result