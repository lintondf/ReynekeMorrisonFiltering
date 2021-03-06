/**
 * 
 */
package com.bluelightning.tools.transpiler;

import org.antlr.v4.runtime.ParserRuleContext;

import com.bluelightning.tools.transpiler.nodes.TranslationNode;

/**
 * @author NOOK
 *
 */
public interface ILanguageTarget {
	
	public boolean isTestTarget();
	
	public void setId(int id);
	
	public int getId();
	
	public void addImport( Scope scope);
	
	public void addParameterClass( String className );
	
	public void startModule( Scope scope, boolean headerOnly, boolean isTest );
	
	public void finishModule();
	
	public void startClass( Scope scope );
	
	public void finishClass( Scope scope );
	
	public void startMethod( Scope scope );
	
	public void finishMethod( Scope scope );
	
	public void startStatement();
	
	public void finishStatement();
	
	public void emitSymbolDeclaration( Symbol symbol, String comment );
	
	public void emitElifStatement(Scope scope, TranslationNode expressionRoot);

	public void emitElseStatement();
	
	public void emitExpressionStatement( Scope scope, TranslationNode root );
	
	public void emitIfStatement(Scope scope, TranslationNode expressionRoot);

	public void emitForStatement(Symbol symbol, TranslationNode expressionRoot);
	
	public void emitNewExpression( Scope scope, String className, TranslationNode root );
	
	public void emitRaiseStatement(String exception);
	
	public void emitReturnStatement(Scope scope, ParserRuleContext ctx, TranslationNode expressionRoot);
	
	public void emitSubExpression( Scope scope, TranslationNode root );
	
	public void closeBlock();
}
