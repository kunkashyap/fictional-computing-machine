import re
import sys

COMP_TABLE = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101",
}

DEST_TABLE = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
}

JUMP_TABLE = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

SYMBOL_PATTERN = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


def default_symbols():
    symbols = {
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
        "SCREEN": 16384,
        "KBD": 24576,
    }
    for i in range(16):
        symbols[f"R{i}"] = i
    return symbols


def parse_c_instruction(line):
    dest = ""
    rest = line

    if "=" in rest:
        parts = rest.split("=")
        if len(parts) != 2:
            return None
        dest, rest = parts[0].strip(), parts[1].strip()
        if not dest:
            return None

    jump = ""
    comp = rest
    if ";" in rest:
        parts = rest.split(";")
        if len(parts) != 2:
            return None
        comp, jump = parts[0].strip(), parts[1].strip()
        if not jump:
            return None

    if not comp:
        return None
    if dest not in DEST_TABLE or comp not in COMP_TABLE or jump not in JUMP_TABLE:
        return None

    return f"111{COMP_TABLE[comp]}{DEST_TABLE[dest]}{JUMP_TABLE[jump]}"


def assemble(asm_path):
    try:
        with open(asm_path, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
    except OSError as e:
        print(f"Error reading file: {e}")
        return

    symbols = default_symbols()
    cleaned = []  # list of (line_num, instruction)
    rom_addr = 0
    errors = []

    # First reading: remove comments and blank lines, record label ROM addresses
    for line_num, raw in enumerate(raw_lines, start=1):
        code = raw.split("//", 1)[0].strip()
        if not code:
            continue

        if code.startswith("(") or code.endswith(")"):
            if not (code.startswith("(") and code.endswith(")")):
                errors.append(f"Line {line_num}: invalid instruction")
                continue
            label = code[1:-1].strip()
            if not SYMBOL_PATTERN.match(label):
                errors.append(f"Line {line_num}: invalid instruction")
                continue
            if label not in symbols:
                symbols[label] = rom_addr
        else:
            cleaned.append((line_num, code))
            rom_addr += 1

    # Second reading: translate instructions and assign variables starting at 16
    next_var_addr = 16
    hack_lines = []

    for line_num, inst in cleaned:
        if inst.startswith("@"):
            target = inst[1:].strip()
            if not target:
                errors.append(f"Line {line_num}: invalid instruction")
                continue

            if target.isdigit():
                value = int(target)
                if value < 0 or value > 32767:
                    errors.append(f"Line {line_num}: invalid instruction")
                    continue
            elif SYMBOL_PATTERN.match(target):
                if target not in symbols:
                    symbols[target] = next_var_addr
                    next_var_addr += 1
                value = symbols[target]
            else:
                errors.append(f"Line {line_num}: invalid instruction")
                continue

            hack_lines.append(f"0{value:015b}")
        else:
            binary = parse_c_instruction(inst)
            if binary is None:
                errors.append(f"Line {line_num}: invalid instruction")
                continue
            hack_lines.append(binary)

    if errors:
        for err in errors:
            print(err)
        return

    out_path = asm_path.rsplit(".", 1)[0] + ".hack" if "." in asm_path else asm_path + ".hack"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(hack_lines) + "\n")

    print(f"Wrote {out_path} ({len(hack_lines)} instructions).")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 assembler.py <program.asm>")
        return
    assemble(sys.argv[1])


if __name__ == "__main__":
    main()