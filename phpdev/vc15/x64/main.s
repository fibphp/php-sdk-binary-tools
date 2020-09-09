	.text
	.def	 @feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
.set @feat.00, 0
	.intel_syntax noprefix
	.file	"main.cpp"
	.def	 main;
	.scl	2;
	.type	32;
	.endef
	.globl	__real@408f400000000000 # -- Begin function main
	.section	.rdata,"dr",discard,__real@408f400000000000
	.p2align	3
__real@408f400000000000:
	.quad	4652007308841189376     # double 1000
	.text
	.globl	main
	.p2align	4, 0x90
main:                                   # @main
# %bb.0:
	push	rbp
	push	rsi
	sub	rsp, 56
	lea	rbp, [rsp + 48]
	movaps	xmmword ptr [rbp - 16], xmm6 # 16-byte Spill
	and	rsp, -16
	call	clock
	mov	esi, eax
	lea	rcx, [rip + "?test_print@@YAXHHH@Z"]
	call	"?test@@YAXHP6AXHHH@Z@Z"
	call	clock
	sub	eax, esi
	cvtsi2sd	xmm1, eax
	movsd	xmm6, qword ptr [rip + __real@408f400000000000] # xmm6 = mem[0],zero
	divsd	xmm1, xmm6
	lea	rcx, [rip + "??_C@_0BH@KNKPEDFK@First?5Used?5?$CFf?5seconds?6?$AA@"]
	movq	rdx, xmm1
	call	printf
	xor	ecx, ecx
	call	"?test@@YAXHP6AXHHH@Z@Z"
	xor	ecx, ecx
	call	"?test@@YAXHP6AXHHH@Z@Z"
	xor	ecx, ecx
	call	"?test@@YAXHP6AXHHH@Z@Z"
	xor	ecx, ecx
	call	"?test@@YAXHP6AXHHH@Z@Z"
	xor	ecx, ecx
	call	"?test@@YAXHP6AXHHH@Z@Z"
	xor	ecx, ecx
	call	"?test@@YAXHP6AXHHH@Z@Z"
	xor	ecx, ecx
	call	"?test@@YAXHP6AXHHH@Z@Z"
	xor	ecx, ecx
	call	"?test@@YAXHP6AXHHH@Z@Z"
	xor	ecx, ecx
	call	"?test@@YAXHP6AXHHH@Z@Z"
	xor	ecx, ecx
	call	"?test@@YAXHP6AXHHH@Z@Z"
	xor	ecx, ecx
	call	"?test@@YAXHP6AXHHH@Z@Z"
	call	clock
	sub	eax, esi
	xorps	xmm1, xmm1
	cvtsi2sd	xmm1, eax
	divsd	xmm1, xmm6
	lea	rcx, [rip + "??_C@_0BF@LLDJHCEH@All?5Used?5?$CFf?5seconds?6?$AA@"]
	movq	rdx, xmm1
	call	printf
	xor	eax, eax
	movaps	xmm6, xmmword ptr [rbp - 16] # 16-byte Reload
	lea	rsp, [rbp + 8]
	pop	rsi
	pop	rbp
	ret
                                        # -- End function
	.def	 "?test@@YAXHP6AXHHH@Z@Z";
	.scl	3;
	.type	32;
	.endef
	.p2align	4, 0x90         # -- Begin function ?test@@YAXHP6AXHHH@Z@Z
"?test@@YAXHP6AXHHH@Z@Z":               # @"?test@@YAXHP6AXHHH@Z@Z"
# %bb.0:
	push	rbp
	push	r15
	push	r14
	push	r13
	push	r12
	push	rsi
	push	rdi
	push	rbx
	sub	rsp, 40
	lea	rbp, [rsp + 32]
	and	rsp, -16
	test	rcx, rcx
	je	.LBB1_10
# %bb.1:
	mov	r14, rcx
	xor	r13d, r13d
	mov	edi, 1000
	jmp	.LBB1_2
	.p2align	4, 0x90
.LBB1_9:                                #   in Loop: Header=BB1_2 Depth=1
	add	r13d, 1
	mov	edi, dword ptr [rsp + 36] # 4-byte Reload
	add	edi, -1
	cmp	r13d, 1001
	je	.LBB1_10
.LBB1_2:                                # =>This Loop Header: Depth=1
                                        #     Child Loop BB1_3 Depth 2
                                        #       Child Loop BB1_4 Depth 3
	mov	r12d, r13d
	imul	r12d, r13d
	mov	dword ptr [rsp + 36], edi # 4-byte Spill
	xor	r15d, r15d
	jmp	.LBB1_3
	.p2align	4, 0x90
.LBB1_8:                                #   in Loop: Header=BB1_3 Depth=2
	add	r15d, 1
	add	edi, -1
	cmp	r15d, 1001
	je	.LBB1_9
.LBB1_3:                                #   Parent Loop BB1_2 Depth=1
                                        # =>  This Loop Header: Depth=2
                                        #       Child Loop BB1_4 Depth 3
	mov	ebx, r15d
	imul	ebx, r15d
	add	ebx, r12d
	xor	esi, esi
	jmp	.LBB1_4
	.p2align	4, 0x90
.LBB1_7:                                #   in Loop: Header=BB1_4 Depth=3
	add	esi, 1
	cmp	esi, 1001
	je	.LBB1_8
.LBB1_4:                                #   Parent Loop BB1_2 Depth=1
                                        #     Parent Loop BB1_3 Depth=2
                                        # =>    This Inner Loop Header: Depth=3
	cmp	edi, esi
	jne	.LBB1_7
# %bb.5:                                #   in Loop: Header=BB1_4 Depth=3
	mov	eax, esi
	imul	eax, esi
	cmp	ebx, eax
	jne	.LBB1_7
# %bb.6:                                #   in Loop: Header=BB1_4 Depth=3
	mov	ecx, r13d
	mov	edx, r15d
	mov	r8d, esi
	call	r14
	jmp	.LBB1_7
.LBB1_10:
	lea	rsp, [rbp + 8]
	pop	rbx
	pop	rdi
	pop	rsi
	pop	r12
	pop	r13
	pop	r14
	pop	r15
	pop	rbp
	ret
                                        # -- End function
	.def	 "?test_print@@YAXHHH@Z";
	.scl	3;
	.type	32;
	.endef
	.p2align	4, 0x90         # -- Begin function ?test_print@@YAXHHH@Z
"?test_print@@YAXHHH@Z":                # @"?test_print@@YAXHHH@Z"
# %bb.0:
	push	rbp
	sub	rsp, 32
	lea	rbp, [rsp + 32]
	and	rsp, -16
	mov	r9d, r8d
	mov	r8d, edx
	mov	edx, ecx
	lea	rcx, [rip + "??_C@_0CB@EHJBANBI@The?5result?5?$CFd?$FO2?5?$CL?5?$CFd?$FO2?5?$DN?5?$CFd?$FO2?5?$CB?6@"]
	call	printf
	mov	rsp, rbp
	pop	rbp
	ret
                                        # -- End function
	.def	 printf;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",discard,printf
	.globl	printf                  # -- Begin function printf
	.p2align	4, 0x90
printf:                                 # @printf
# %bb.0:
	push	rbp
	push	rsi
	push	rdi
	push	rbx
	sub	rsp, 56
	lea	rbp, [rsp + 48]
	and	rsp, -16
	mov	rsi, rcx
	mov	qword ptr [rbp + 56], rdx
	mov	qword ptr [rbp + 64], r8
	mov	qword ptr [rbp + 72], r9
	lea	rbx, [rbp + 56]
	mov	qword ptr [rsp + 48], rbx
	mov	ecx, 1
	call	__acrt_iob_func
	mov	rdi, rax
	call	__local_stdio_printf_options
	mov	rcx, qword ptr [rax]
	mov	qword ptr [rsp + 32], rbx
	mov	rdx, rdi
	mov	r8, rsi
	xor	r9d, r9d
	call	__stdio_common_vfprintf
	lea	rsp, [rbp + 8]
	pop	rbx
	pop	rdi
	pop	rsi
	pop	rbp
	ret
                                        # -- End function
	.def	 __local_stdio_printf_options;
	.scl	2;
	.type	32;
	.endef
	.section	.text,"xr",discard,__local_stdio_printf_options
	.globl	__local_stdio_printf_options # -- Begin function __local_stdio_printf_options
	.p2align	4, 0x90
__local_stdio_printf_options:           # @__local_stdio_printf_options
# %bb.0:
	push	rbp
	mov	rbp, rsp
	and	rsp, -8
	lea	rax, [rip + "?_OptionsStorage@?1??__local_stdio_printf_options@@9@4_KA"]
	mov	rsp, rbp
	pop	rbp
	ret
                                        # -- End function
	.section	.rdata,"dr",discard,"??_C@_0BH@KNKPEDFK@First?5Used?5?$CFf?5seconds?6?$AA@"
	.globl	"??_C@_0BH@KNKPEDFK@First?5Used?5?$CFf?5seconds?6?$AA@" # @"??_C@_0BH@KNKPEDFK@First?5Used?5?$CFf?5seconds?6?$AA@"
"??_C@_0BH@KNKPEDFK@First?5Used?5?$CFf?5seconds?6?$AA@":
	.asciz	"First Used %f seconds\n"

	.section	.rdata,"dr",discard,"??_C@_0BF@LLDJHCEH@All?5Used?5?$CFf?5seconds?6?$AA@"
	.globl	"??_C@_0BF@LLDJHCEH@All?5Used?5?$CFf?5seconds?6?$AA@" # @"??_C@_0BF@LLDJHCEH@All?5Used?5?$CFf?5seconds?6?$AA@"
"??_C@_0BF@LLDJHCEH@All?5Used?5?$CFf?5seconds?6?$AA@":
	.asciz	"All Used %f seconds\n"

	.section	.rdata,"dr",discard,"??_C@_0CB@EHJBANBI@The?5result?5?$CFd?$FO2?5?$CL?5?$CFd?$FO2?5?$DN?5?$CFd?$FO2?5?$CB?6@"
	.globl	"??_C@_0CB@EHJBANBI@The?5result?5?$CFd?$FO2?5?$CL?5?$CFd?$FO2?5?$DN?5?$CFd?$FO2?5?$CB?6@" # @"??_C@_0CB@EHJBANBI@The?5result?5?$CFd?$FO2?5?$CL?5?$CFd?$FO2?5?$DN?5?$CFd?$FO2?5?$CB?6@"
"??_C@_0CB@EHJBANBI@The?5result?5?$CFd?$FO2?5?$CL?5?$CFd?$FO2?5?$DN?5?$CFd?$FO2?5?$CB?6@":
	.asciz	"The result %d^2 + %d^2 = %d^2 !\n"

	.section	.bss,"bw",discard,"?_OptionsStorage@?1??__local_stdio_printf_options@@9@4_KA"
	.globl	"?_OptionsStorage@?1??__local_stdio_printf_options@@9@4_KA" # @"?_OptionsStorage@?1??__local_stdio_printf_options@@9@4_KA"
	.p2align	3
"?_OptionsStorage@?1??__local_stdio_printf_options@@9@4_KA":
	.quad	0                       # 0x0

	.section	.drectve,"yn"
	.ascii	" /FAILIFMISMATCH:\"_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\""
	.addrsig
	.addrsig_sym "?test_print@@YAXHHH@Z"
	.addrsig_sym "?_OptionsStorage@?1??__local_stdio_printf_options@@9@4_KA"
	.globl	_fltused
