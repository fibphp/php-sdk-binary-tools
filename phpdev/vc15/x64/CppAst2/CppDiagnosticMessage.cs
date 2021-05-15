// Copyright (c) Alexandre Mutel. All rights reserved.
// Licensed under the BSD-Clause 2 license.
// See license.txt file in the project root for full license information.

using System;
using CppAst2;

namespace CppAst2
{
    public enum CppLogMessageType
    {
        Info = 0,
        Warning = 1,
        Error = 2,
    }

    /// <summary>
    /// Provides a diagnostic message for a specific location in the source code.
    /// </summary>
    public class CppDiagnosticMessage
    {
        public CppDiagnosticMessage(CppLogMessageType type, string text, CppSourceLocation location)
        {
            if (text == null) throw new ArgumentNullException(nameof(text));
            Type = type;
            Text = text;
            Location = location;
        }

        public readonly CppLogMessageType Type;

        public readonly string Text;

        public readonly CppSourceLocation Location;

        public override string ToString()
        {
            return $"{Location}: {Type.ToString().ToLowerInvariant()}: {Text}";
        }
    }
}