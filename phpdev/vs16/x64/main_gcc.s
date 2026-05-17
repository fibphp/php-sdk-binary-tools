	.file	"main.cpp"
	.text
	.p2align 4
	.def	_ZL4testiPFviiiE.constprop.0;	.scl	3;	.type	32;	.endef
	.seh_proc	_ZL4testiPFviiiE.constprop.0
_ZL4testiPFviiiE.constprop.0:
.LFB105:
	.seh_endprologue
	ret
	.seh_endproc
	.section	.text$_Z6printfPKcz,"x"
	.linkonce discard
	.p2align 4
	.globl	_Z6printfPKcz
	.def	_Z6printfPKcz;	.scl	2;	.type	32;	.endef
	.seh_proc	_Z6printfPKcz
_Z6printfPKcz:
.LFB8:
	pushq	%r12
	.seh_pushreg	%r12
	pushq	%rbx
	.seh_pushreg	%rbx
	subq	$56, %rsp
	.seh_stackalloc	56
	.seh_endprologue
	leaq	88(%rsp), %rbx
	movq	%rdx, 88(%rsp)
	movq	%rcx, %r12
	movl	$1, %ecx
	movq	%r8, 96(%rsp)
	movq	%r9, 104(%rsp)
	movq	%rbx, 40(%rsp)
	call	*__imp___acrt_iob_func(%rip)
	movq	%rbx, %r8
	movq	%r12, %rdx
	movq	%rax, %rcx
	call	__mingw_vfprintf
	addq	$56, %rsp
	popq	%rbx
	popq	%r12
	ret
	.seh_endproc
	.section .rdata,"dr"
	.align 8
.LC0:
	.ascii "The result %d^2 + %d^2 = %d^2 !\12\0"
	.text
	.p2align 4
	.def	_ZL10test_printiii;	.scl	3;	.type	32;	.endef
	.seh_proc	_ZL10test_printiii
_ZL10test_printiii:
.LFB102:
	.seh_endprologue
	movl	%r8d, %r9d
	movl	%edx, %r8d
	movl	%ecx, %edx
	leaq	.LC0(%rip), %rcx
	jmp	_Z6printfPKcz
	.seh_endproc
	.p2align 4
	.def	_ZL4testiPFviiiE.constprop.1;	.scl	3;	.type	32;	.endef
	.seh_proc	_ZL4testiPFviiiE.constprop.1
_ZL4testiPFviiiE.constprop.1:
.LFB104:
	pushq	%r13
	.seh_pushreg	%r13
	pushq	%r12
	.seh_pushreg	%r12
	pushq	%rbp
	.seh_pushreg	%rbp
	pushq	%rdi
	.seh_pushreg	%rdi
	pushq	%rsi
	.seh_pushreg	%rsi
	pushq	%rbx
	.seh_pushreg	%rbx
	subq	$40, %rsp
	.seh_stackalloc	40
	.seh_endprologue
	xorl	%r13d, %r13d
	.p2align 4,,10
	.p2align 3
.L9:
	movl	%r13d, %r12d
	movl	%r13d, %esi
	xorl	%edi, %edi
	imull	%r13d, %r12d
	.p2align 4,,10
	.p2align 3
.L8:
	movl	%edi, %ebp
	xorl	%ebx, %ebx
	imull	%edi, %ebp
	addl	%r12d, %ebp
	jmp	.L7
	.p2align 4,,10
	.p2align 3
.L6:
	addl	$1, %ebx
	cmpl	$1001, %ebx
	je	.L13
.L7:
	leal	(%rbx,%rsi), %eax
	cmpl	$1000, %eax
	jne	.L6
	movl	%ebx, %eax
	imull	%ebx, %eax
	cmpl	%eax, %ebp
	jne	.L6
	movl	%ebx, %r8d
	movl	%edi, %edx
	movl	%r13d, %ecx
	addl	$1, %ebx
	call	_ZL10test_printiii
	cmpl	$1001, %ebx
	jne	.L7
	.p2align 4,,10
	.p2align 3
.L13:
	addl	$1, %edi
	addl	$1, %esi
	cmpl	$1001, %edi
	jne	.L8
	addl	$1, %r13d
	cmpl	$1001, %r13d
	jne	.L9
	addq	$40, %rsp
	popq	%rbx
	popq	%rsi
	popq	%rdi
	popq	%rbp
	popq	%r12
	popq	%r13
	ret
	.seh_endproc
	.def	__main;	.scl	2;	.type	32;	.endef
	.section .rdata,"dr"
.LC2:
	.ascii "First Used %f seconds\12\0"
.LC3:
	.ascii "All Used %f seconds\12\0"
	.section	.text.startup,"x"
	.p2align 4
	.globl	main
	.def	main;	.scl	2;	.type	32;	.endef
	.seh_proc	main
main:
.LFB103:
	pushq	%rbx
	.seh_pushreg	%rbx
	subq	$48, %rsp
	.seh_stackalloc	48
	movaps	%xmm6, 32(%rsp)
	.seh_savexmm	%xmm6, 32
	.seh_endprologue
	call	__main
	call	clock
	movl	%eax, %ebx
	call	_ZL4testiPFviiiE.constprop.1
	call	clock
	pxor	%xmm1, %xmm1
	movsd	.LC1(%rip), %xmm6
	leaq	.LC2(%rip), %rcx
	subl	%ebx, %eax
	cvtsi2sdl	%eax, %xmm1
	divsd	%xmm6, %xmm1
	movq	%xmm1, %rdx
	call	_Z6printfPKcz
	call	clock
	pxor	%xmm1, %xmm1
	leaq	.LC3(%rip), %rcx
	subl	%ebx, %eax
	cvtsi2sdl	%eax, %xmm1
	divsd	%xmm6, %xmm1
	movq	%xmm1, %rdx
	call	_Z6printfPKcz
	nop
	movaps	32(%rsp), %xmm6
	xorl	%eax, %eax
	addq	$48, %rsp
	popq	%rbx
	ret
	.seh_endproc
	.section .rdata,"dr"
	.align 8
.LC1:
	.long	0
	.long	1083129856
	.ident	"GCC: (Rev5, Built by MSYS2 project) 10.3.0"
	.def	__mingw_vfprintf;	.scl	2;	.type	32;	.endef
	.def	clock;	.scl	2;	.type	32;	.endef
