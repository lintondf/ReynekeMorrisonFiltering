/**
 * 
 */
package com.bluelightning.tools.transpiler.nodes;

import org.antlr.v4.runtime.ParserRuleContext;

/**
 * @author NOOK
 *
 */
public class TranslationConstantNode extends TranslationSubexpressionNode {

	String value;
	
	public enum Kind { INTEGER, FLOAT, STRING };
	Kind   kind;
	
	public TranslationConstantNode(ParserRuleContext ctx, TranslationNode parent, String value, Kind kind) {
		super(ctx, parent, "<CONSTANT>:" + kind.toString() + " = " + value);
		this.value = value;
		this.kind = kind;
		switch (kind) {
		case INTEGER:
			setType("int");
			break;
		case FLOAT:
			setType("float");
			break;
		case STRING:
			setType("str");
			break;
		}
	}

	public String getValue() {
		return value;
	}

	public Kind getKind() {
		return kind;
	}

}
