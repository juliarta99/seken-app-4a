import os

def load_words(filename):
    """Membaca file txt dari folder alphabets dan mengembalikan list kata"""
    try:
        filepath = os.path.join("alphabets", filename)
        
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read().split("\n")
            clean_content = [word.strip() for word in content if word.strip()]
            return clean_content
            
    except FileNotFoundError:
        print(f"Warning: File {filename} tidak ditemukan.")
        return []

print("Sedang memuat kamus kata...")
kata_benda         = load_words("noun.txt")
proper_noun        = load_words("propnoun.txt")
kata_ganti         = load_words("pronoun.txt")
kata_preposisi     = load_words("prep.txt")
kata_sifat         = load_words("adj.txt")
determinan         = load_words("det.txt")
numeralia          = load_words("num.txt")
adverbia           = load_words("adv.txt")
verb               = load_words("verb.txt")
kata_benda_waktu   = load_words("nountime.txt")

alphabet = (
    kata_benda + 
    proper_noun + 
    kata_ganti + 
    kata_preposisi + 
    kata_sifat + 
    determinan + 
    numeralia + 
    adverbia + 
    verb +
    kata_benda_waktu
)

print(f"Berhasil memuat {len(alphabet)} kata ke dalam alphabet.")

def check_alphabet(input_array):
    """
    Mengecek apakah setiap kata dalam input_array ada di dalam alphabet.
    Mengembalikan tuple: (is_known: bool, unknown_words: list)
    
    Args:
        input_array (list): Array kata yang akan dicek
    
    Returns:
        tuple: (bool, list) - (True jika semua kata dikenali, list kata yang tidak dikenali)
    """
    unknown_words = []
    
    for kata in input_array:
        # Cek
        if kata.lower() not in alphabet:
            unknown_words.append(kata)
    
    if unknown_words:
        print(f"Error: Kata tidak ditemukan dalam kamus: {', '.join(unknown_words)}")
        return False, unknown_words
    
    return True, []