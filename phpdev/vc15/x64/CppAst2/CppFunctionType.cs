﻿// Copyright (c) Alexandre Mutel. All rights reserved.
// Licensed under the BSD-Clause 2 license.
// See license.txt file in the project root for full license information.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace CppAst2
{
    /// <summary>
    /// A C++ function type (e.g `void (*)(int arg1, int arg2)`)
    /// </summary>
    public sealed class CppFunctionType : CppTypeDeclaration
    {
        /// <summary>
        /// Constructor of a function type.
        /// </summary>
        /// <param name="returnType">Return type of this function type.</param>
        public CppFunctionType(CppType returnType) : base(CppTypeKind.Function)
        {
            ReturnType = returnType ?? throw new ArgumentNullException(nameof(returnType));
            Parameters = new CppContainerList<CppParameter>(this);
        }

        /// <summary>
        /// Gets or sets the calling convention of this function type.
        /// </summary>
        public CppCallingConvention CallingConvention { get; set; }

        /// <summary>
        /// Gets or sets the return type of this function type.
        /// </summary>
        public CppType ReturnType { get; set; }
        
        /// <summary>
        /// Gets a list of the parameters.
        /// </summary>
        public CppContainerList<CppParameter> Parameters { get; }

        private bool Equals(CppFunctionType other)
        {
            if (base.Equals(other) && ReturnType.Equals(other.ReturnType))
            {
                if (Parameters.Count != other.Parameters.Count)
                {
                    return false;
                }

                for (int i = 0; i < Parameters.Count; i++)
                {
                    var fromType = Parameters[i].Type;
                    var otherType = other.Parameters[i].Type;
                    if (!fromType.Equals(otherType))
                    {
                        return false;
                    }
                }

                return true;
            }

            return false;
        }

        public override int SizeOf
        {
            get => 0;
            
            set => throw new InvalidOperationException("This type does not support SizeOf");
        }

        public override bool Equals(object obj)
        {
            return ReferenceEquals(this, obj) || obj is CppFunctionType other && Equals(other);
        }

        public override int GetHashCode()
        {
            unchecked
            {
                int hashCode = base.GetHashCode();
                hashCode = (hashCode * 397) ^ ReturnType.GetHashCode();
                foreach (var parameter in Parameters)
                {
                    hashCode = (hashCode * 397) ^ parameter.Type.GetHashCode();
                }
                return hashCode;
            }
        }

        public override IEnumerable<ICppDeclaration> Children()
        {
            return Parameters;
        }

        public override CppType GetCanonicalType()
        {
            return this;
        }

        public override string ToString()
        {
            var builder = new StringBuilder();
            builder.Append(ReturnType.GetDisplayName());
            builder.Append(" ");
            builder.Append("(*)(");
            for (var i = 0; i < Parameters.Count; i++)
            {
                var param = Parameters[i];
                if (i > 0) builder.Append(", ");
                builder.Append(param);
            }

            builder.Append(")");
            return builder.ToString();
        }
    }
}