﻿// Copyright (c) Alexandre Mutel. All rights reserved.
// Licensed under the BSD-Clause 2 license.
// See license.txt file in the project root for full license information.

using System;

namespace CppAst2
{
    /// <summary>
    /// A C++ pointer type (e.g `int*`)
    /// </summary>
    public sealed class CppPointerType : CppTypeWithElementType
    {
        /// <summary>
        /// Constructor of a pointer type.
        /// </summary>
        /// <param name="elementType">The element type pointed to.</param>
        public CppPointerType(CppType elementType) : base(CppTypeKind.Pointer, elementType)
        {
            SizeOf = IntPtr.Size;
        }

        public override string ToString()
        {
            return $"{ElementType.GetDisplayName()}*";
        }

        public override CppType GetCanonicalType()
        {
            var elementTypeCanonical = ElementType.GetCanonicalType();
            if (ReferenceEquals(elementTypeCanonical, ElementType)) return this;
            return new CppPointerType(elementTypeCanonical);
        }
    }
}