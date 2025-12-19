//20616323 Xiaoyu SHEN

//pseudocode:
//X=R0
//Y=R1
//if X&1+Y&1==0 goto EVEN.EVEN
//if X&1+Y&1==1 goto ODD.EVEN
//if X&1+Y&1==2 goto ODD.ODD
//
//EVEN.EVEN:
//  if X>=0 goto EE.NNEGATIVE
//      if X+Y>0 goto EE.GREATER
//      if X+Y<0 goto EE.LESS
//      if X+Y==0 goto SORT
//  EE.GREATER:
//      R2=X
//      interval_value=-X
//      EE.G.LOOP:
//          R2=R2+interval_value
//          interval_value=interval_value+2
//          if interval_value<=Y goto EE.G.LOOP
//      goto SORT
//  EE.LESS:
//      R2=Y
//      interval_value=-Y
//      EE.L.LOOP:
//          R2=R2+interval_value
//          interval_value=interval_value-2
//          if interval_value>X goto EE.L.LOOP
//      goto SORT
//  EE.NNEGATIVE:
//      interval_value=X
//      EE.LOOP:
//          R2=R2+interval_value
//          interval_value=interval_value+2
//          if interval_value<=Y goto EE.LOOP
//      goto SORT
//
//ODD.EVEN:
//  interval_value=X
//  OE.LOOP:
//      interval_value=interval_value+1 (see implementation detail: start from X-1 then ++ once per loop)
//      R2=R2+interval_value
//      if interval_value<=Y goto OE.LOOP
//  goto SORT
//
//ODD.ODD:
//  if X>=0 goto OO.NNEGATIVE
//      if X+Y>0 goto OO.GREATER
//      if X+Y<0 goto OO.LESS
//      if X+Y==0 goto SORT
//  OO.GREATER:
//      R2=X
//      interval_value=-X
//      OO.G.LOOP:
//          R2=R2+interval_value
//          interval_value=interval_value+2
//          if interval_value<=Y goto OO.G.LOOP
//      goto SORT
//  OO.LESS:
//      R2=Y
//      interval_value=-Y
//      OO.L.LOOP:
//          R2=R2+interval_value
//          interval_value=interval_value-2
//          if interval_value>=X goto OO.L.LOOP
//      goto SORT
//  OO.NNEGATIVE:
//      interval_value=X
//      OO.LOOP:
//          R2=R2+interval_value
//          interval_value=interval_value+2
//          if interval_value<=Y goto OO.LOOP
//      goto SORT
//
//SORT:
//  max=0
//  min=1000
//  sum=R2
//  bucket[-100..100]=0
//  if R2>0 goto P.SORT
//  if R2<0 goto N.SORT
//  if R2==0 goto STOP
//
//P.SORT:
//  i=array
//  P.I.LOOP:
//      array_value=RAM[i]
//      bucket[array_value]=bucket[array_value]+1
//      if array_value<=max goto P.NGREATER 
//          max=array_value
//      P.NGREATER:
//      if array_value>=min goto P.NLESS
//          min=array_value
//      P.NLESS:
//      i=i+1
//      if i<sum goto P.I.LOOP
//
//  pointer=array
//  j=min
//  P.J.LOOP
//      if bucket[j]<=0 goto P.NEXIST
//          RAM[pointer]=bucket[j]
//          pointer=pointer+1
//          bucket[j]=bucket[j]-1
//      P.NEXIST:
//      j=j+1
//      if j<=max goto P.J.LOOP
//  goto STOP
//
//N.SORT:
//  i=array
//  sum=-sum
//  N.I.LOOP:
//      array_value=RAM[i]
//      bucket[array_value]=bucket[array_value]+1
//      if array_value<=max goto N.NGREATER 
//          max=array_value
//      N.NGREATER:
//      if array_value>=min goto N.NLESS
//          min=array_value
//      N.NLESS:
//      i=i+1
//      if i<sum goto N.I.LOOP
//
//  pointer=array
//  j=max
//  N.J.LOOP:
//      if bucket[j]<=0 goto N.NEXIST
//          RAM[pointer]=bucket[j]
//          pointer=pointer+1
//          bucket[j]=bucket[j]-1
//      N.NEXIST:
//      j=j-1
//      if j>=min goto N.J.LOOP
//  goto STOP
//STOP:
//



// declare the address of the array that needs to be sorted
@50
D=A
@array_address
M=D

// declare the parity checker to check the parity of X and Y.
@1
D=A
@parity_checker
M=D

// initialize sum register R2 to 0 to avoid undefined accumulation
@0
D=A
@R2
M=D

// check the parity of X and save the result in R3
@R0
D=M  // D = R0
@parity_checker
D=D&M   // D = R0 & 1
@R3
M=D

// check parity of Y and accumulate
@R1
D=M
@parity_checker
D=D&M   // D = R1 & 1
@R3
D=D+M   // D = (X&1) + (Y&1)

// branch by parity sum: 0 -> EVEN.EVEN, 1 -> ODD.EVEN, 2 -> ODD.ODD
@EVEN.EVEN
D=D-1;JLT

@ODD.ODD
D;JGT

@ODD.EVEN
D;JEQ



// EVEN.EVEN
(EVEN.EVEN)
    @R0
    D=M
    @EE.NNEGATIVE
    D;JGE
        @R1
        D=D+M      // D = X + Y

        @EE.GREATER
        D;JGT
        @EE.LESS
        D;JLT

        // X + Y == 0 => sum is 0
        @SORT
        D;JEQ

        (EE.GREATER)
            @R0
            D=M
            @R2
            M=D       // pre-add X
            D=-D
            @interval_value
            M=D

            (EE.G.LOOP)
                @interval_value
                D=M
                @R2
                M=M+D
                @interval_value
                D=M+1
                M=D+1
                @R1
                D=M-D
            @EE.G.LOOP
            D;JGE
            @SORT
            0;JMP

        (EE.LESS)
            @R1
            D=M
            @R2
            M=D       // pre-add Y
            D=-D
            @interval_value
            M=D

            (EE.L.LOOP)
                @interval_value
                D=M
                @R2
                M=M+D
                @interval_value
                D=M-1
                M=D-1
                @R0
                D=M-D
            @EE.L.LOOP
            D;JLE
            @SORT
            0;JMP

    (EE.NNEGATIVE)
    @R0
    D=M
    @interval_value
    M=D

    (EE.LOOP)
        @interval_value
        D=M
        @R2
        M=M+D
        @interval_value
        D=M+1
        M=D+1
        @R1
        D=M-D
    @EE.LOOP
    D;JGE
    @SORT
    0;JMP



// ODD.EVEN — unified implementation: sum all integers from X to Y inclusive, step +1
(ODD.EVEN)
    @R0
    D=M
    @interval_value
    M=D-1       // start from X-1, then ++ once per loop

    (OE.LOOP)
        @interval_value
        M=M+1    // interval_value = interval_value + 1
        D=M
        
        // 先检查是否超出范围
        @R1
        D=D-M    // D = interval_value - Y
        @SORT
        D;JGT    // if interval_value > Y, exit to SORT
        
        // 未超出，累加
        @interval_value
        D=M
        @R2
        M=M+D    // R2 += interval_value

    @OE.LOOP
    0;JMP    // 无条件跳回循环开始



// ODD.ODD
(ODD.ODD)
    @R0
    D=M
    @OO.NNEGATIVE
    D;JGE
        @R1
        D=D+M     // D = X + Y

        @OO.GREATER
        D;JGT
        @OO.LESS
        D;JLT
        @SORT
        D;JEQ

        (OO.GREATER)
            @R0
            D=M
            @R2
            M=D
            @interval_value
            M=-D

            (OO.G.LOOP)
                @interval_value
                D=M
                @R2
                M=M+D
                @interval_value
                D=M+1
                M=D+1
                @R1
                D=M-D
            @OO.G.LOOP
            D;JGE
            @SORT
            0;JMP

        (OO.LESS)
            @R1
            D=M
            @R2
            M=D
            D=-D
            @interval_value
            M=D

            (OO.L.LOOP)
                @interval_value
                D=M
                @R2
                M=M+D
                @interval_value
                D=M-1
                M=D-1
                @R0
                D=M-D
            @OO.L.LOOP
            D;JLE
            @SORT
            0;JMP

    (OO.NNEGATIVE)
    @R0
    D=M
    @interval_value
    M=D

    (OO.LOOP)
        @interval_value
        D=M
        @R2
        M=M+D
        @interval_value
        D=M+1
        M=D+1
        @R1
        D=M-D
    @OO.LOOP
    D;JGE
    @SORT
    0;JMP



// SORT (bucket sort)
(SORT)
    @200
    D=A
    @offset
    M=D

    @0
    D=A
    @max
    M=D

    @1000
    D=A
    @min
    M=D

    @array_address
    D=M
    @sum
    M=D
    @R2
    D=M
    @sum
    M=M+D

    @P.SORT
    D;JGT

    @N.SORT
    D;JLT

    @STOP
    D;JEQ



(P.SORT)
    @array_address
    D=M
    @i
    M=D

    (P.I.LOOP)
        @i
        D=M
        A=D
        D=M
        @offset
        D=D+M
        @array_value
        M=D
        A=D
        M=M+1

        @max
        D=D-M
        @P.NGREATER
        D;JLE
            @max
            M=D+M
        (P.NGREATER)

        @array_value
        D=M
        @min
        D=D-M
        @P.NLESS
        D;JGE
            @min
            M=D+M
        (P.NLESS)

        @i
        M=M+1
        D=M
        @sum
        D=D-M
    @P.I.LOOP
    D;JLT

    @array_address
    D=M
    @pointer
    M=D

    @min
    D=M
    @j
    M=D

    (P.J.LOOP)
        @j
        A=M
        D=M
        @P.NEXIST
        D;JEQ

            @j
            A=M
            M=M-1

            @offset
            D=M
            @j
            D=M-D

            @pointer
            M=M+1
            A=M-1
            M=D

            @j
            M=M-1
        (P.NEXIST)

        @j
        M=M+1
        D=M
        @max
        D=D-M
    @P.J.LOOP
    D;JLE

    @STOP
    0;JMP



(N.SORT)
    @array_address
    D=M
    @i
    M=D

    @R2
    D=M-D
    @sum
    M=D

    (N.I.LOOP)
        @i
        D=M
        A=D
        D=M
        @offset
        D=D+M
        @array_value
        M=D
        A=D
        M=M+1

        @max
        D=D-M
        @N.NGREATER
        D;JLE
            @max
            M=D+M
        (N.NGREATER)

        @array_value
        D=M
        @min
        D=D-M
        @N.NLESS
        D;JGE
            @min
            M=D+M
        (N.NLESS)

        @i
        M=M+1
        D=M
        @sum
        D=D+M
    @N.I.LOOP
    D;JLT

    @array_address
    D=M
    @pointer
    M=D

    @max
    D=M
    @j
    M=D

    (N.J.LOOP)
        @j
        A=M
        D=M
        @N.NEXIST
        D;JEQ

            @j
            A=M
            M=M-1

            @offset
            D=M
            @j
            D=M-D

            @pointer
            M=M+1
            A=M-1
            M=D

            @j
            M=M+1
        (N.NEXIST)

        @j
        M=M-1
        D=M
        @min
        D=D-M
    @N.J.LOOP
    D;JGE

    @STOP
    0;JMP



(STOP)
@STOP
0;JMP