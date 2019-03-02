package com.bluelightning.tools.transpiler;

import java.util.HashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.antlr.v4.runtime.CommonToken;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.RuleNode;

import com.bluelightning.tools.transpiler.Scope.Level;
import com.bluelightning.tools.transpiler.TranslationConstantNode.Kind;
import com.bluelightning.tools.transpiler.antlr4.LcdPythonBaseListener;
import com.bluelightning.tools.transpiler.antlr4.LcdPythonParser;

class ExpressionCompilationListener extends LcdPythonBaseListener {
		
		/**
		 * 
		 */
		private final Transpiler transpiler;
		Scope scope = null;
		TranslationNode expressionRoot = null;
		HashMap<Object, TranslationNode> translateMap = null;
		
		
		/**
		 * @param transpiler
		 */
		ExpressionCompilationListener(Transpiler transpiler) {
			this.transpiler = transpiler;
			scope = this.transpiler.moduleScope;
			transpiler.logger.info("module > " + scope);
		}
		
		protected static final Pattern integerPattern = Pattern.compile("^(\\d+)$");
		protected static final Pattern floatPattern = Pattern.compile("^(\\d+)\\.(\\\\d*)$");
		
		protected TranslationNode defaultOperandOperator( ParserRuleContext ctx, String tag ) {
			if (expressionRoot != null) {
//				System.out.println( tag + " (" + ctx.getChildCount() + ")");
//				transpiler.dumpChildren(ctx);
				TranslationNode parent = new TranslationSubexpressionNode(null, tag);
				if (ctx.getChildCount() == 1) {
					TranslationNode node = translateMap.get(ctx.getChild(0).getPayload());
					if (node == null) {
						node = getOperandNode( ctx, parent, ctx.getChild(0).getPayload());
						if (node == null) {
							String operator = this.transpiler.valueMap.get(ctx.getChild(0).getPayload());
							node = new TranslationOperatorNode( parent, operator );
						}
					}
					translateMap.put( ctx.getPayload(), node );
					parent.analyze();
					return node;
				} else if (ctx.getChildCount() == 2) {
					transpiler.dumpChildren(ctx);
					TranslationNode node = new TranslationUnaryNode( parent, 
							ctx.getChild(0).getPayload(), ctx.getChild(1).getPayload());
				} else {
					TranslationNode node = getOperandNode( ctx, parent, ctx.getChild(0).getPayload());
					if (node == null) {
						String value = this.transpiler.valueMap.get(ctx.getChild(0).getPayload());
						this.transpiler.reportError(ctx, "Operand neither symbol nor constant nor subexpression: " + 
								ctx.getChild(0).getPayload().getClass().getSimpleName() + " : " + value);

					}
					for (int i = 1; i < ctx.getChildCount(); i += 2) {
						String operator = this.transpiler.valueMap.get(ctx.getChild(i).getPayload());
						if (operator.startsWith(".")) {
//							transpiler.dumpChildren((RuleNode) ctx.getChild(i) );
							Symbol symbol = transpiler.symbolTable.lookup(scope, operator.substring(1));
							node = new TranslationUnaryNode( parent, ctx.getChild(i).getChild(0).getPayload(), symbol );
						} else {
							node = new TranslationOperatorNode( parent, operator );
						}
						node = getOperandNode( ctx, parent, ctx.getChild(i+1).getPayload());
						if (node == null) {
							transpiler.reportError(ctx, "No operand node: " + (i+1));
						}
					}
				}
//				parent.traverse(2); /////////////
				translateMap.put( ctx.getPayload(), parent );
				parent.analyze();
				return parent;
			}	
			return null;
		}
		
		protected TranslationNode getOperandNode(ParserRuleContext context, TranslationNode parent, Object payload) {
			String value = this.transpiler.valueMap.get(payload);
			TranslationNode node = translateMap.get(payload);
			if (node != null) {
				parent.adopt( node );
				return node;
			}
			Symbol symbol = this.transpiler.symbolTable.lookup( scope, value );
			if (symbol != null) {
				node = new TranslationSymbolNode( parent, symbol );
				translateMap.put( payload, node );
				return node;
			}
			if (value.startsWith("'") || value.startsWith("\"")) {
				node = new TranslationConstantNode( parent, value, Kind.STRING );
				translateMap.put( payload, node );
				return node;
			}
			Matcher matcher = integerPattern.matcher(value);
			if (matcher.matches()) {
				node = new TranslationConstantNode( parent, value, Kind.INTEGER );
				translateMap.put( payload, node );
				return node;				
			}
			matcher = floatPattern.matcher(value);
			if (matcher.matches()) {
				node = new TranslationConstantNode( parent, value, Kind.FLOAT );
				translateMap.put( payload, node );
				return node;				
			}
			return null;
		}

		@Override
		public void enterClassdef(LcdPythonParser.ClassdefContext ctx) {
			scope = this.transpiler.scopeMap.get(ctx.getPayload());
//			System.out.println("class > " + scope);
			transpiler.dispatcher.startClass(scope);
		}
		
		@Override
		public void exitClassdef(LcdPythonParser.ClassdefContext ctx) {
			scope = scope.getParent();
//			System.out.println("class < " + scope);
			transpiler.dispatcher.finishClass(scope);
		}
		
		@Override
		public void enterFuncdef(LcdPythonParser.FuncdefContext ctx) {
			scope = this.transpiler.scopeMap.get(ctx.getPayload());
//			System.out.println("function > " + scope);
			transpiler.dispatcher.startMethod(scope);
		}
		
		@Override
		public void exitFuncdef(LcdPythonParser.FuncdefContext ctx) {
			scope = scope.getParent();
//			System.out.println("function < " + scope);
			transpiler.dispatcher.finishMethod(scope);
		}
		
		@Override 
		public void enterReturn_stmt(LcdPythonParser.Return_stmtContext ctx) {
			expressionRoot = new TranslationSubexpressionNode(null, "RETURN_STMT");
			translateMap = new HashMap<>();
			
		}
		
		//raise_stmt: 'raise' (test ('from' test)?)?;
		@Override 
		public void exitRaise_stmt(LcdPythonParser.Raise_stmtContext ctx) { 
		}
		
		// return_stmt: 'return' (testlist)?;
		@Override 
		public void exitReturn_stmt(LcdPythonParser.Return_stmtContext ctx) { 
			transpiler.dispatcher.emitReturnStatement();
			if (ctx.getChildCount() > 1) {
				expressionRoot = translateMap.get( ctx.getChild(1).getPayload() );
				System.out.println("RETURN< " + expressionRoot.toString() );
				System.out.println( expressionRoot.traverse(1));
				transpiler.dispatcher.emitSubExpression(scope, expressionRoot);
				transpiler.dispatcher.emitCloseStatement();
			}
			expressionRoot = null;
		}
		
		
		@Override
		public void enterExpr_stmt(LcdPythonParser.Expr_stmtContext ctx) {
			String value = this.transpiler.valueMap.get(ctx.getPayload());
			if (! value.startsWith("'''")) {
				System.out.println("EXPR_STMT> [{" + value + "}] <- " + ctx.toStringTree(transpiler.parser));
//				this.transpiler.dumpChildren( ctx, 1 );
				expressionRoot = new TranslationSubexpressionNode(null, value);
				translateMap = new HashMap<>();
			} else if (value.startsWith("'''@")) {
				value = value.trim().replaceAll(" +", "");
				String[] fields = value.substring(4).replaceAll("'''", "").split("-"); // drop any comments
				fields = fields[0].split(":");
				Symbol symbol = transpiler.symbolTable.lookup(scope, fields[0]);
				if (symbol != null) {
					transpiler.dispatcher.emitSymbolDeclaration(symbol);
				}
			}
		}

		@Override
		public void exitExpr_stmt(LcdPythonParser.Expr_stmtContext ctx) {
			if (expressionRoot != null) {
				TranslationNode expr = defaultOperandOperator( ctx, expressionRoot.name );
				expr.analyze();
				expressionRoot = expr;
//				System.out.println("EXPR_STMT< " + expr.toString() );
//				System.out.println( expr.traverse(1));
				while (expressionRoot.getChildCount() == 1) {
					expr = expressionRoot.getChild(0);
					if (expr.getChildCount() == 0)
						break;
					expressionRoot = expr;
				}
				if ( ! transpiler.valueMap.get(ctx.getPayload()).startsWith("'''@")) {
//					System.out.println( expr.traverse(1));
					transpiler.dispatcher.emitExpressionStatement(scope, expressionRoot);
				} else {
					//TODO docstring?
				}
			}
			expressionRoot = null;
		}		
		
		@Override
		public void exitAnnassign(LcdPythonParser.AnnassignContext ctx) {
			defaultOperandOperator( ctx, "Annassign" );
		}

		@Override 
		public void exitArglist(LcdPythonParser.ArglistContext ctx) { 
//			transpiler.dumpChildren(ctx);
			defaultOperandOperator( ctx, "arglist" );
		}
		
		@Override 
		public void exitArgument(LcdPythonParser.ArgumentContext ctx) { 
			defaultOperandOperator( ctx, "argument" );
		}
		
		@Override
		public void exitTestlist_star_expr(LcdPythonParser.Testlist_star_exprContext ctx) {
			defaultOperandOperator( ctx, "testlist_expr" );
		}

//		@Override 
//		public void exitTrailer(LcdPythonParser.TrailerContext ctx) { 
////			transpiler.dumpChildren(ctx);
//			//defaultOperandOperator( ctx, "trailer" );	
//			String operator = transpiler.valueMap.get(ctx.getChild(0).getPayload());
//			TranslationSubexpressionNode parent = new TranslationListNode(null, operator);
//			TranslationNode node = null;
//			switch (operator) {
//			case "(": // function argument list
//			case "[": // array subscripts
//				if (ctx.getChildCount() > 2) {
//					ParseTree list = ctx.getChild(1);
//					for (int i = 0; i < list.getChildCount(); i += 2) {
//						node = getOperandNode(ctx, parent, list.getChild(i).getPayload());
//						if (node == null) {
//							transpiler.reportError("Untranlated: " + list.getChild(i).toStringTree(transpiler.parser) );
//						}
//						parent.adopt(node);
//					}
//				}
//				break;
//			case ".": // member access
//				String name = transpiler.valueMap.get(ctx.getChild(1).getPayload());
//				Symbol field = transpiler.symbolTable.lookup(scope, name);
//				if (field == null) {
//					if (parent.getLastChild() instanceof TranslationSymbolNode) {
//						TranslationSymbolNode tsn = (TranslationSymbolNode) parent.getLastChild();
//						if (tsn.getSymbol().getType().equals("<ENUM>")) {
//							Scope enumScope = tsn.getSymbol().getScope().getChild(Level.CLASS, tsn.getSymbol().getName());
//							field = transpiler.symbolTable.lookup(enumScope, name );
//							System.out.println("ENUM> " + field.toString());
//						}
//					}
//					if (field == null)
//						transpiler.reportError("Undeclared member: " + name + " " + scope );
//				}
//				node = new TranslationUnaryNode( parent, name, field );
//				translateMap.put( ctx.getPayload(), node );
//				return;
//			default:
//				transpiler.reportError(ctx, "Unknown Trailer starting token: " + operator );
//				break;
//			}
//			translateMap.put( ctx.getPayload(), parent );
//			parent.analyze();
//		}	
		
		@Override
		public void exitAugassign(LcdPythonParser.AugassignContext ctx) {
			defaultOperandOperator( ctx, "augassign" );
		}

		@Override
		public void exitTest(LcdPythonParser.TestContext ctx) {
			defaultOperandOperator( ctx, "test" );
		}

		@Override
		public void exitTest_nocond(LcdPythonParser.Test_nocondContext ctx) {
			defaultOperandOperator( ctx, "test_nocond" );
		}

		@Override
		public void exitOr_test(LcdPythonParser.Or_testContext ctx) {
			defaultOperandOperator( ctx, "or_test" );
		}

		@Override
		public void exitAnd_test(LcdPythonParser.And_testContext ctx) {
			defaultOperandOperator( ctx, "and_test" );
		}

		@Override
		public void exitNot_test(LcdPythonParser.Not_testContext ctx) {
			defaultOperandOperator( ctx, "not_test"  );
		}

		@Override
		public void exitComparison(LcdPythonParser.ComparisonContext ctx) {
			defaultOperandOperator( ctx, "comparison" );
		}

		@Override
		public void exitComp_op(LcdPythonParser.Comp_opContext ctx) {
			defaultOperandOperator( ctx, "comp_op" );
		}

		@Override
		public void exitExpr(LcdPythonParser.ExprContext ctx) {
			defaultOperandOperator( ctx, "exitexpr" );
		}

		@Override
		public void exitXor_expr(LcdPythonParser.Xor_exprContext ctx) {
			defaultOperandOperator( ctx, "xor_expr" );
		}

		@Override
		public void exitAnd_expr(LcdPythonParser.And_exprContext ctx) {
			defaultOperandOperator( ctx, "and_expr" );
		}

		@Override
		public void exitShift_expr(LcdPythonParser.Shift_exprContext ctx) {
			defaultOperandOperator( ctx, "shift_expr" );
		}

		//arith_expr: term (('+'|'-') term)*;
		@Override
		public void exitArith_expr(LcdPythonParser.Arith_exprContext ctx) {
			defaultOperandOperator( ctx, "Arith_expr" );
		}
		
		@Override
		public void exitTerm(LcdPythonParser.TermContext ctx) {
			defaultOperandOperator( ctx, "Term" );
		}

		@Override
		public void exitFactor(LcdPythonParser.FactorContext ctx) {
			defaultOperandOperator( ctx, "factor" );
		}

		@Override
		public void exitPower(LcdPythonParser.PowerContext ctx) {
			defaultOperandOperator( ctx, "power" );
		}

//atom_expr: (AWAIT)? atom trailer*;
//trailer: '(' (arglist)? ')' | '[' subscriptlist ']' | '.' NAME;		
		@Override
		public void exitAtom_expr(LcdPythonParser.Atom_exprContext ctx) {
			if (ctx.getChildCount() == 1) {
				defaultOperandOperator( ctx, "atom_expr" );
			} else {
				TranslationNode parent = new TranslationSubexpressionNode(null, "atom_expr");
				Symbol symbol = transpiler.symbolTable.lookup(scope, ctx.getChild(0).getText() );
				if (symbol == null) {
					transpiler.reportError("Unknown symbol: " + ctx.getChild(0).getText() + " " + scope);
					return;
				}
				new TranslationSymbolNode( parent, symbol );
				for (int iTrailer = 0; iTrailer < ctx.getChildCount(); iTrailer++) {
					ParseTree trailer = ctx.getChild(iTrailer);
					for (int i = 0; i < trailer.getChildCount(); i++) {
						String unary = trailer.getChild(i).getText().substring(0,1); 
						switch (unary) {
						case "(":
						case "[":
							if (ctx.getChildCount() > 2) {
								ParseTree list = trailer.getChild(1);
								for (int iList = 0; iList < list.getChildCount(); iList += 2) {
									TranslationNode node = getOperandNode(ctx, parent, list.getChild(iList).getPayload());
									if (node == null) {
										transpiler.reportError("Untranlated: " + list.getChild(iList).toStringTree(transpiler.parser) );
									}
									parent.adopt(node);
								}
							}
//							TranslationListNode list = new TranslationListNode( parent, unary );
//							for (int j = 1; j < trailer.getChildCount()-1; j++) {
//								System.out.println(unary + " " + trailer.getChild(j).getText() );
//								list.adopt(translateMap.get(trailer.getChild(j).getPayload()));
//							}
							break;
						case ".":
							Symbol field = transpiler.symbolTable.lookup(scope, trailer.getChild(i+1).getText());
							if (field == null) {
								if (parent.getLastChild() instanceof TranslationSymbolNode) {
									TranslationSymbolNode tsn = (TranslationSymbolNode) parent.getLastChild();
									if (tsn.getSymbol().getType().equals("<ENUM>")) {
										Scope enumScope = tsn.getSymbol().getScope().getChild(Level.CLASS, tsn.getSymbol().getName());
										field = transpiler.symbolTable.lookup(enumScope, trailer.getChild(i+1).getText() );
										System.out.println("ENUM> " + field.toString());
									}
								}
							}
							new TranslationUnaryNode( parent, trailer.getChild(i).getPayload(), field );
							break;
						}
					}
				}
				this.translateMap.put( ctx.getPayload(), parent);
			}
		}

//atom: ('(' (yield_expr|testlist_comp)? ')' |                      2 () or 3 (x)
//       '[' (testlist_comp)? ']' |
//       '{' (dictorsetmaker)? '}' |
//       NAME | NUMBER | STRING+ | '...' | 'None' | 'True' | 'False');
		@Override
		public void exitAtom(LcdPythonParser.AtomContext ctx) {
//			transpiler.dumpChildren(ctx);
			if (expressionRoot != null) {
				TranslationNode parent = new TranslationSubexpressionNode(null, "atom");
				Object payload = ctx.getChild(0).getPayload();
				TranslationNode node = getOperandNode( ctx, parent, payload);
				if (node != null && ctx.getChildCount() == 1) {  // NAME | NUMBER |  '...' | 'None' | 'True' | 'False'
					if (parent.getChildCount() == 1) {
						parent = parent.getChild(0);
					}
					translateMap.put( ctx.getPayload(), parent );
					parent.analyze();
					return;
				}
				if (node != null) { // STRING+ 
					for (int i = 1; i < ctx.getChildCount(); i++) {
						payload = ctx.getChild(i).getPayload();
						getOperandNode( ctx, parent, payload);
					}
					if (parent.getChildCount() == 1) {
						parent = parent.getChild(0);
					}
					translateMap.put( ctx.getPayload(), parent );
					parent.analyze();
					return;
				}
				String value = transpiler.valueMap.get(payload);
				if (value.length() != 1 || "([{".indexOf(value) == -1) {
					//transpiler.reportError(ctx, "Unexpected ATOM token: " + value );
					return;
				}
				parent = new TranslationListNode( null, value);
				for (int i = 1; i < ctx.getChildCount()-1; i++) {
					payload = ctx.getChild(i).getPayload();
					node = translateMap.get(payload);
					if (node == null) {
						node = getOperandNode(ctx, parent, payload);
					}
					parent.adopt(node);
				}
				translateMap.put( ctx.getPayload(), parent );
				parent.analyze();
			}
		}
		
		@Override
		public void exitSubscriptlist(LcdPythonParser.SubscriptlistContext ctx) {
			defaultOperandOperator( ctx, "subscriptlist" );
		}

		@Override
		public void exitSubscript(LcdPythonParser.SubscriptContext ctx) {
			defaultOperandOperator( ctx, "subscript" );
		}

		@Override
		public void exitSliceop(LcdPythonParser.SliceopContext ctx) {
			defaultOperandOperator( ctx, "sliceop" );
		}

		@Override
		public void exitExprlist(LcdPythonParser.ExprlistContext ctx) {
			defaultOperandOperator( ctx, "exprlist" );
		}

		@Override
		public void exitTestlist(LcdPythonParser.TestlistContext ctx) {
			defaultOperandOperator( ctx, "testlist" );
		}

		@Override 
		public void exitTestlist_comp(LcdPythonParser.Testlist_compContext ctx) { 
			defaultOperandOperator( ctx, "testlist_comp" );
		}
		
		@Override
		public void exitDictorsetmaker(LcdPythonParser.DictorsetmakerContext ctx) {
			defaultOperandOperator( ctx, "dictorsetmaker" );
		}

	}