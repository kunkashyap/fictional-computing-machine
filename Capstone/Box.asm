// Draws a 16px (1-word) wide by 20-row high box at row 88 (address 19200)
// when any key is pressed (KBD != 0), and clears it when no key is pressed.

(LOOP)
    // Check keyboard state at RAM[24576]
    @KBD
    D=M
    @DRAW_BLACK
    D;JNE       // If key pressed (D != 0), draw black (-1)
    @DRAW_WHITE
    0;JMP       // Otherwise, draw white (0)

(DRAW_BLACK)
    @color
    M=-1        // -1 = 1111111111111111 (all 16 pixels black)
    @START_DRAW
    0;JMP

(DRAW_WHITE)
    @color
    M=0         // 0 = 0000000000000000 (all 16 pixels white)

(START_DRAW)
    // Initialize current address to row 88 left word (16384 + 32*88 = 19200)
    @19200
    D=A
    @addr
    M=D

    // Initialize row counter to 20 rows
    @20
    D=A
    @rows
    M=D

(ROW_LOOP)
    // Stop when rows == 0
    @rows
    D=M
    @LOOP
    D;JEQ

    // Load chosen color (-1 or 0) and write to RAM[addr]
    @color
    D=M
    @addr
    A=M
    M=D

    // Move down one screen row (+32 words)
    @32
    D=A
    @addr

    // Decrement remaining row count
    @rows
    M=M-1

    @ROW_LOOP
    0;JMP