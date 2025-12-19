// 测试ODD.EVEN逻辑
// X=1 (R0), Y=4 (R1)

@1
D=A
@R0
M=D

@4
D=A
@R1
M=D

@0
D=A
@R2
M=D

// ODD.EVEN部分
@R0
D=M
@interval_value
M=D-1       // interval_value = 0

(OE.LOOP)
    @interval_value
    M=M+1    // interval_value++
    D=M      // D = interval_value
    @R2
    M=M+D    // R2 += interval_value

    @R1
    D=M-D    // D = Y - interval_value (问题在这里！)
@OE.LOOP
D;JGE

(STOP)
@STOP
0;JMP
