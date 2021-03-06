package com.bluelightning.tools.transpiler.java.programmer;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.ejml.data.DMatrixRMaj;
import org.ejml.dense.row.CommonOps_DDRM;
import org.ejml.equation.CompileCodeOperations;
import org.ejml.equation.EmitJavaOperation;
import org.ejml.equation.Equation;
import org.ejml.equation.GenerateEquationCode;
import org.ejml.equation.IEmitOperation;
import org.ejml.equation.IOperationFactory;
import org.ejml.equation.Info;
import org.ejml.equation.ManagerFunctions;
import org.ejml.equation.ManagerTempVariables;
import org.ejml.equation.OperationCodeFactory;
import org.ejml.equation.Sequence;
import org.ejml.equation.Variable;
import org.ejml.equation.VariableDouble;
import org.ejml.equation.VariableInteger;
import org.ejml.equation.VariableMatrix;
import org.ejml.equation.VariableScalar;
import org.ejml.equation.Info.Operation;

import com.bluelightning.tools.transpiler.IProgrammer;
import com.bluelightning.tools.transpiler.IProgrammer.IExpressionCompiler;
import com.bluelightning.tools.transpiler.Scope;
import com.bluelightning.tools.transpiler.Scope.Level;
import com.bluelightning.tools.transpiler.Symbol;
import com.bluelightning.tools.transpiler.SymbolTable;
import com.bluelightning.tools.transpiler.Transpiler;
import com.bluelightning.tools.transpiler.java.AbstractJavaTarget;
import com.bluelightning.tools.transpiler.java.AbstractJavaTarget.StaticImport;

public class EjmlExpressionCompiler implements IExpressionCompiler {
	
	private class JavaTargetManagerFunctions extends ManagerFunctions {
		
		AbstractProgrammer programmer;
		ManagerTempVariables tempManager;
		
		public JavaTargetManagerFunctions( IOperationFactory factory, ManagerTempVariables tempManager, AbstractProgrammer programmer ) {
			super(factory);
			this.programmer = programmer;
			this.tempManager = tempManager;
			new CopyFunction().add();
			new MaxFunction().add();
			new MinFunction().add();
			new NumRowsFunction().add();
			new NumElementsFunction().add();
			new NumColsFunction().add();
	    	new IdentityFunction().add();
	    	new IntFunction().add();
	    	new PrintFunction().add();
	    	new ReturnFunction().add();
	    	new TransposeFunction().add();
	    	new VoidFunction().add();
	    	new ZerosFunction().add();
	    	// test functions
	    	new AssertAlmostEqualFunction().add();
		}
		
		void add( GenericMethodFunction gmf ) {
			addN( gmf.opName(), gmf, gmf );
		}
		
		
		private boolean printMapping = false; 
		
		protected void mapUsage( Symbol symbol, SymbolTable symbolTable ) {
			if (symbol.getType().equals("array")) {
//				System.out.printf("    builtin %s: %s\n", symbol.getName(), "array");
				for (IProgrammer.Pair pair : programmer.getMatrixMethods()) {
					String name = programmer.rewriteSymbol(symbol.getScope(), symbol) + "$" + pair.methodName;
//					System.out.printf("      method %s: %s\n", name, pair.methodType);
			    	GenericMethodFunction gmf = new GenericMethodFunction(name, pair.methodType);
			    	add( gmf );
				}
			} else if (symbol.getType().equals("vector")) {
//				System.out.printf("    builtin %s: %s\n", symbol.getName(), "vector");
				for (IProgrammer.Pair pair : programmer.getVectorMethods()) {
					String name = programmer.rewriteSymbol(symbol.getScope(), symbol) + "$" + pair.methodName;
//					System.out.printf("      method %s: %s\n", name, pair.methodType);
			    	GenericMethodFunction gmf = new GenericMethodFunction(name, pair.methodType);
			    	add( gmf );
				}						
			} else {
				Symbol c = Transpiler.instance().lookupClass(symbol.getType());
				if (c != null) {
					Scope objectClass = c.getScope().getChild(Level.CLASS, c.getName());
					if (printMapping) System.out.printf("    object %s: %s; %s\n", symbol.getName(), c.toString(), objectClass.toString());
//					if (symbol.getScope().toString().contains("Fmp_test") &&
//							symbol.getName().equals("testData")) {
//						System.out.println(objectClass.toAnnotatedString());
//					}
					for (Symbol method : symbolTable.atScope(objectClass)) {
						if (method.isFunction()) {
							if (method.getName().equals("__init__"))
								continue;
							String name = method.getName();
							if (! method.isStatic())
								name = programmer.rewriteSymbol(symbol.getScope(), symbol) + "$" + name;
							if (printMapping) System.out.printf("      method %s: %s\n", name, method.getType());
					    	GenericMethodFunction gmf = new GenericMethodFunction(name, method.getType());
				    		add( gmf );
						}
					}
				}
			}
		}
		
		public void mapFunctions( Scope scope, SymbolTable symbolTable, boolean isTest ) {
			//printMapping = scope.toString().equals("/polynomialfiltering/components/Fmp_test/test1CheckStates/");
			while (scope.getLevelCount() > 0) {
				if (printMapping) System.out.println("AT: " + scope.toString());
				for (Symbol symbol : symbolTable.atScope(scope)) {
					if (printMapping) System.out.println( (symbol.isFunction() ? "  FUNCTION: " : "  SYMBOL: ") + symbol.getName() );
					if (symbol.isFunction()) {
						for (Symbol local : symbolTable.atScope(symbol.getScope())) {
							if (local.isFunction())
								continue;
							if (printMapping) System.out.println("    LOCAL: " + local.getName());
							mapUsage( local, symbolTable );
						}
					} else {
						if (printMapping) System.out.println("    VARIABLE: " + symbol.getName());
						mapUsage( symbol, symbolTable );						
					}
				}
				scope = scope.getParent();
			} // while ascending levels
			
			if (! isTest) {
				List<Symbol> statics = Transpiler.instance().getSymbolTable().getStaticFunctions();
				for (Symbol method : statics) {
					if (method.getName().equals("__init__"))
						continue;
					Symbol symbol = Transpiler.instance().lookupClass(method.getScope().getLast());
					if (symbol == null)
						continue;
					String name = programmer.rewriteSymbol(method.getScope().getParent(), symbol) + "$" + method.getName();
//					System.out.printf("      method %s: %s\n", name, method.getType());
			    	GenericMethodFunction gmf = new GenericMethodFunction(name, method.getType());
		    		add( gmf );
				}
			}
		}
		
		
		public String declare( Variable variable ) {
			if (variable.isConstant())
				return "";
			switch (variable.getType()) {
			case SCALAR:
				VariableScalar scalar = (VariableScalar) variable;
				if (scalar.getScalarType() == VariableScalar.Type.INTEGER) {
					return( "int ");
				} else {
					return( "double " );    					
				}
			case MATRIX:
				return( programmer.getMatrixClass() + " " );
			default:
				return "";
			}
		}
		
		
		public class GenericMethodFunction implements ManagerFunctions.InputN, ManagerFunctions.Coder {
			
			private String name;
			private String type;
			//private Variable output;
			
			public GenericMethodFunction(String name, String type ) {
				this.name = name;
				this.type = type;
			}

			@Override
			public String code(Info info) {
				StringBuilder sb = new StringBuilder();
				if (info.output.isTemp()) {
					declaredTemps.add(info.output.getOperand());
					sb.append( declare(info.output) );
				}
				if ( ! info.output.getOperand().equals("void")) {
					sb.append(info.output.getOperand());
					sb.append(" = ");
				}
				sb.append(name);
				sb.append("(");
				for (int i = 0; i < info.input.size(); i++) {
					Variable v = info.input.get(i);
					sb.append(v.getOperand());
					if (i < info.input.size()-1) 
						sb.append(", ");
				}
				sb.append(");\n");
				return sb.toString();
			}

			@Override
			public String opName() {
				return name;
			}

			@Override
			public Info create(List<Variable> inputs, ManagerTempVariables manager) {
				final Info info = new Info(inputs);
				switch (type) {
				case "int":
					info.output = tempManager.createInteger();
					break;
				case "float":
					info.output = tempManager.createDouble();
					break;
				case "array":
					info.output = tempManager.createMatrix();
					break;
				case "vector":
					info.output = tempManager.createMatrix();
					break;
				case "None":
					info.output = tempManager.createIntegerConstant(0, "void");
					break;
				default:
					info.output = tempManager.createInteger(); //
				}
				info.op = info.new Operation(opName()) {
					@Override
					public void process() {
					}
				};
				return info;
			}
			
		}
		
		public abstract class CodedFunction1 implements ManagerFunctions.Input1, ManagerFunctions.Coder {
			public String name;
			
			CodedFunction1(String name) {
				this.name = name;
			}

			public void add() {
				add1( name, this, this);
			}
		}
		
		public abstract class CodedFunctionN implements ManagerFunctions.InputN, ManagerFunctions.Coder {
			public String name;
			
			CodedFunctionN(String name) {
				this.name = name;
			}
			
			public void add() {
				addN( name, this, this);
			}
		}
		
		/*
	    public class X extends CodedFunction1 {
	    	X() {
				super("");
			}

			@Override
			public String opName() {
				return "$-";
			} 

			@Override
			public Info create(Variable A, ManagerTempVariables manager) {
		    	final Info info = new Info(A);
		    	if( A instanceof VariableMatrix ) {
		    		info.output = manager.createInteger();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
						}
		    		};
		    	} else {
		    		throw new RuntimeException("numCols only takes one matrix parameter");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				return sb.toString();
			}
	    }
		 */
		
		
	    public class AssertAlmostEqualFunction extends CodedFunctionN {
	    	
	    	String opname;
	    	
	    	AssertAlmostEqualFunction() {
				super("assert_almost_equal");
			}
	    	
			@Override
			public Info create(List<Variable> inputs, ManagerTempVariables manager) {
		    	final Info info = new Info();
		    	info.input = inputs;
		    	if (info.input.size() == 2) {
		    		info.output = manager.createIntegerConstant(0, "void");
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
						}
		    		};
		    	} else {
		    		throw new RuntimeException("assert_almost_equal requires exactly two parameters");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				sb.append( String.format("assert_almost_equal(%s, %s);\n",
						info.input.get(0).getOperand(),
						info.input.get(1).getOperand() ) );
				return sb.toString();
			}

			@Override
			public String opName() {
				return opname;
			}

			@Override
			public void add() {
				String[] opnames = {"assert_almost_equal-ss", "assert_almost_equal-mm"};
				for (String n : opnames) {
					opname = n;
					super.add();
				}
			}
	    }
	    
	    
	    public class CopyFunction extends CodedFunction1 {
	    	CopyFunction() {
				super("copy");
			}

			@Override
			public String opName() {
				return "$copy-m";
			} 

			@Override
			public Info create(Variable A, ManagerTempVariables manager) {
		    	final Info info = new Info(A);
		    	if( A instanceof VariableMatrix ) {
		    		info.output = manager.createMatrix();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
							VariableMatrix M = ((VariableMatrix) info.input.get(0));
		                    info.outputMatrix().matrix.reshape(M.matrix.numRows, M.matrix.numCols);
		                    CommonOps_DDRM.scale(1.0, M.matrix, info.outputMatrix().matrix);
						}
		    		};
		    	} else {
		    		throw new RuntimeException("copy only takes one matrix parameter");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				if (info.output.isTemp() && ! declaredTemps.contains(info.output.getOperand())) {
					declaredTemps.add(info.output.getOperand());
					sb.append( String.format("DMatrixRMaj %s = new DMatrixRMaj(%s);\n", 
						info.output.getOperand(), A.getOperand()));
				} else {
					 sb.append( String.format(EmitJavaOperation.formatCommonOps3, "scale", "1.0", A.getOperand(), info.output.getOperand()) );
				}
				return sb.toString();
			}
	    }
	    
	    public class IdentityFunction extends CodedFunction1 {
			IdentityFunction() {
				super("identity");
			}

			@Override
			public String opName() {
				return "$identity-i";
			} 

			@Override
			public Info create(Variable A, ManagerTempVariables manager) {
		    	final Info info = new Info(A);
		    	if( A instanceof VariableInteger ) {
		    		info.output = manager.createMatrix();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
		                    int N = ((VariableInteger) info.input.get(0)).value;
		                    info.outputMatrix().matrix.reshape(N,N);
		                    CommonOps_DDRM.setIdentity(info.outputMatrix().matrix);
						}
		    		};
		    	} else {
		    		throw new RuntimeException("identity only takes one integer parameter");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				sb.append( String.format("%s.reshape(%s, %s);\n", info.output.getOperand(), A.getOperand(), A.getOperand()) );
				//CommonOps_DDRM.setIdentity(output.matrix);
				sb.append( String.format(EmitJavaOperation.formatCommonOps1, "setIdentity", info.output.getOperand()) );
				return sb.toString();
			}
	    }
	    
	    public class IntFunction extends CodedFunction1 {
	    	IntFunction() {
				super("int");
			}

			@Override
			public String opName() {
				return "$int-s";
			} 

			@Override
			public Info create(Variable A, ManagerTempVariables manager) {
		    	final Info info = new Info(A);
		    	if( A instanceof VariableScalar ) {
		    		info.output = manager.createInteger();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
							info.outputInteger().value = (int) ((VariableScalar) info.A()).getDouble();
						}
		    		};
		    	} else {
		    		throw new RuntimeException("int() only takes one scalar parameter");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				sb.append(String.format("%s = (int) %s;\n", info.output.getOperand(), info.A().getOperand()));
				return sb.toString();
			}
	    }
	    
	    public class MaxFunction extends CodedFunctionN {
	    	MaxFunction() {
				super("max");
			}

			@Override
			public String opName() {
				return "$max-s";
			} 

			@Override
			public Info create(List<Variable> inputs, ManagerTempVariables manager) {
		    	final Info info = new Info();
		    	info.input = inputs;
		    	if (info.input.size() == 2) {
		    		info.output = manager.createDouble();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
							info.outputDouble().value = Math.max(
										((VariableScalar) info.input.get(0)).getDouble(),
										((VariableScalar) info.input.get(1)).getDouble() );
						}
		    		};
		    	} else {
		    		throw new RuntimeException("max requires exactly two parameters");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				sb.append( String.format("%s = Math.max(%s, %s);\n",
							info.outputDouble().getOperand(), 
							((VariableScalar) info.input.get(0)).getOperand(),
							((VariableScalar) info.input.get(1)).getOperand() ));
				return sb.toString();
			}
	    }
	    
	    public class MinFunction extends CodedFunctionN {
	    	MinFunction() {
				super("min");
			}

			@Override
			public String opName() {
				return "$min-s";
			} 

			@Override
			public Info create(List<Variable> inputs, ManagerTempVariables manager) {
		    	final Info info = new Info();
		    	info.input = inputs;
		    	if (info.input.size() == 2) {
		    		if (info.input.get(0) instanceof VariableInteger && info.input.get(1) instanceof VariableInteger) {
			    		info.output = manager.createInteger();
			    		info.op = info.new Operation(opName()) {
							@Override
							public void process() {
								info.outputInteger().value = Math.min(
											((VariableInteger) info.input.get(0)).value,
											((VariableInteger) info.input.get(1)).value );
							}
			    		};
		    		} else {
			    		info.output = manager.createDouble();
			    		info.op = info.new Operation(opName()) {
							@Override
							public void process() {
								info.outputDouble().value = Math.min(
											((VariableScalar) info.input.get(0)).getDouble(),
											((VariableScalar) info.input.get(1)).getDouble() );
							}
			    		};
		    		}
		    	} else {
		    		throw new RuntimeException("min requires exactly two parameters");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				sb.append( String.format("%s = Math.min(%s, %s);\n",
							info.output.getOperand(), 
							((VariableScalar) info.input.get(0)).getOperand(),
							((VariableScalar) info.input.get(1)).getOperand() ));
				return sb.toString();
			}
	    }
	    
	    public class NumColsFunction extends CodedFunction1 {
	    	NumColsFunction() {
				super("numCols");
			}

			@Override
			public String opName() {
				return "$numCols-m";
			} 

			@Override
			public Info create(Variable A, ManagerTempVariables manager) {
		    	final Info info = new Info(A);
		    	if( A instanceof VariableMatrix ) {
		    		info.output = manager.createInteger();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
		                    CommonOps_DDRM.setIdentity(info.outputMatrix().matrix);
		                    info.outputInteger().value = ((VariableMatrix) info.A()).matrix.getNumCols();
						}
		    		};
		    	} else {
		    		throw new RuntimeException("numCols only takes one matrix parameter");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				sb.append( String.format("%s = %s.getNumCols();\n", info.output.getOperand(), A.getOperand()) );
				return sb.toString();
			}
	    }
	    
	    public class NumElementsFunction extends CodedFunction1 {
	    	NumElementsFunction() {
				super("numElements");
			}

			@Override
			public String opName() {
				return "$numElements-m";
			} 

			@Override
			public Info create(Variable A, ManagerTempVariables manager) {
		    	final Info info = new Info(A);
		    	if( A instanceof VariableMatrix ) {
		    		info.output = manager.createInteger();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
		                    CommonOps_DDRM.setIdentity(info.outputMatrix().matrix);
		                    info.outputInteger().value = ((VariableMatrix) info.A()).matrix.getNumElements();
						}
		    		};
		    	} else {
		    		throw new RuntimeException("numElements only takes one matrix parameter");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				sb.append( String.format("%s = %s.getNumElements();\n", info.output.getOperand(), A.getOperand()) );
				return sb.toString();
			}
	    }
	    
	    public class NumRowsFunction extends CodedFunction1 {
	    	NumRowsFunction() {
				super("numRows");
			}

			@Override
			public String opName() {
				return "$numRows-m";
			} 

			@Override
			public Info create(Variable A, ManagerTempVariables manager) {
		    	final Info info = new Info(A);
		    	if( A instanceof VariableMatrix ) {
		    		info.output = manager.createInteger();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
		                    CommonOps_DDRM.setIdentity(info.outputMatrix().matrix);
		                    info.outputInteger().value = ((VariableMatrix) info.A()).matrix.getNumRows();
						}
		    		};
		    	} else {
		    		throw new RuntimeException("numRows only takes one matrix parameter");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				sb.append( String.format("%s = %s.getNumRows();\n", info.output.getOperand(), A.getOperand()) );
				return sb.toString();
			}
	    }
	    
	    public class PrintFunction extends CodedFunction1 {
	    	
	    	String opname;
	    	Pattern variablePattern = Pattern.compile("\\w");
	    	
	    	@Override
			public void add() {
	    		String[] opnames = {"$print-s", "$print-m"};
	    		for (String n : opnames) {
	    			opname = n;
	    			super.add();
	    		}
			}

	    	PrintFunction() {
				super("print");
			}

			@Override
			public String opName() {
				return opname;
			} 

			@Override
			public Info create(Variable A, ManagerTempVariables manager) {
		    	final Info info = new Info(A);
		    	if( info.input.size() == 1 ) {
		    		info.output = manager.createInteger();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
						}
		    		};
		    	} else {
		    		throw new RuntimeException("print() only takes one parameter");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				sb.append(String.format("//System.out.println( %s );", A.getOperand()));
				return sb.toString();
			}
	    }
	    
	    public class ReturnFunction extends CodedFunction1 {
	    	
	    	String opname;
	    	Pattern variablePattern = Pattern.compile("\\w");
	    	
	    	@Override
			public void add() {
	    		String[] opnames = {"$return-s", "$return-m"};
	    		for (String n : opnames) {
	    			opname = n;
	    			super.add();
	    		}
			}

	    	ReturnFunction() {
				super("return");
			}

			@Override
			public String opName() {
				return opname;
			} 

			@Override
			public Info create(Variable A, ManagerTempVariables manager) {
		    	final Info info = new Info(A);
		    	if( info.input.size() == 1 ) {
		    		info.output = manager.createInteger();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
						}
		    		};
		    	} else {
		    		throw new RuntimeException("return() only takes one parameter");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				sb.append(String.format("return %s;", A.getOperand()));
				return sb.toString();
			}
	    }
	    
	    public class TransposeFunction extends CodedFunction1 {
	    	TransposeFunction() {
				super("transpose");
			}

			@Override
			public String opName() {
				return "$transpose-m";
			} 

			@Override
			public Info create(Variable A, ManagerTempVariables manager) {
		    	final Info info = new Info(A);
		    	if( A instanceof VariableMatrix ) {
		    		info.output = manager.createMatrix();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
							VariableMatrix M = ((VariableMatrix) info.input.get(0));
		                    info.outputMatrix().matrix.reshape(M.matrix.numRows, M.matrix.numCols);
		                    CommonOps_DDRM.transpose(M.matrix, info.outputMatrix().matrix);
						}
		    		};
		    	} else {
		    		throw new RuntimeException("transpose only takes one matrix parameter");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
				if (info.output.isTemp() && ! declaredTemps.contains(info.output.getOperand())) {
					sb.append( String.format("DMatrixRMaj %s = new DMatrixRMaj(%s.getNumCols(), %s.getNumRows());\n", 
						info.output.getOperand(), A.getOperand(), A.getOperand()));
					declaredTemps.add(info.output.getOperand());
				} else {
					sb.append( String.format("%s.reshape( %s.numCols, %s.numRows );\n", info.output.getOperand(), A.getOperand(), A.getOperand()));
				}
				sb.append( String.format(EmitJavaOperation.formatCommonOps2, "transpose", A.getOperand(), info.output.getOperand()) );
				return sb.toString();
			}
	    }
	    
	    public class VoidFunction extends CodedFunction1 {
	    	
	    	String opname;
	    	Pattern variablePattern = Pattern.compile("\\w");
	    	
	    	@Override
			public void add() {
	    		String[] opnames = {"$void-s", "$void-m"};
	    		for (String n : opnames) {
	    			opname = n;
	    			super.add();
	    		}
			}

			VoidFunction() {
				super("void");
			}

			@Override
			public String opName() {
				return opname;
			} 

			@Override
			public Info create(Variable A, ManagerTempVariables manager) {
		    	final Info info = new Info(A);
		    	if( info.input.size() == 1 ) {
		    		info.output = manager.createInteger();
		    		info.op = info.new Operation(opName()) {
						@Override
						public void process() {
						}
		    		};
		    	} else {
		    		throw new RuntimeException("void() only takes one parameter");
		    	}
	    		return info;
			}

			@Override
			public String code(Info info) {
				Variable A = info.input.get(0);
				StringBuilder sb = new StringBuilder();
//				if (! info.A().getOperand().equals("void")) {
//					sb.append(String.format("%s;\n", info.A().getOperand()));
//				}
				return sb.toString();
			}
	    }
	    
	    public class ZerosFunction extends CodedFunctionN {
			ZerosFunction() {
				super("zeros");
			}

			@Override
			public String opName() {
				return "$zeros-i";
			} 

			@Override
			public Info create(List<Variable> inputs, ManagerTempVariables manager) {
				if (inputs.size() == 1) {
			    	final Info info = new Info(inputs.get(0));
			    	if( info.A() instanceof VariableInteger ) {
			    		info.output = manager.createMatrix();
			    		info.op = info.new Operation(opName()) {
							@Override
							public void process() {
			                    int N = ((VariableInteger) info.input.get(0)).value;
			                    info.outputMatrix().matrix.reshape(N,1);
			                    CommonOps_DDRM.fill(info.outputMatrix().matrix, 0.0);
							}
			    		};
			    		return info;
			    	}
				} else if (inputs.size() == 2) {
			    	final Info info = new Info(inputs.get(0), inputs.get(1));
			    	if( info.A() instanceof VariableInteger && info.B() instanceof VariableInteger) {
			    		info.output = manager.createMatrix();
			    		info.op = info.new Operation(opName()) {
							@Override
							public void process() {
			                    int N = ((VariableInteger) info.input.get(0)).value;
			                    int M = ((VariableInteger) info.input.get(1)).value;
			                    info.outputMatrix().matrix.reshape(N,M);
			                    CommonOps_DDRM.fill(info.outputMatrix().matrix, 0.0);
							}
			    		};
			    		return info;
			    	}
			    }
		    	throw new RuntimeException("zeros only takes one or two integer parametes");
			}

			@Override
			public String code(Info info) {
				StringBuilder sb = new StringBuilder();
				if (info.input.size() == 1) {
					sb.append( String.format("%s.reshape(%s, %s);\n", info.output.getOperand(), info.A().getOperand(), "1") );
				} else {
					sb.append( String.format("%s.reshape(%s, %s);\n", info.output.getOperand(), info.A().getOperand(), info.B().getOperand()) );					
				}
				//CommonOps_DDRM.setIdentity(output.matrix);
				sb.append( String.format(EmitJavaOperation.formatCommonOps2, "fill", info.output.getOperand(), "0.0") );
				return sb.toString();
			}
	    }
	    
	    ////CommonOps_DDRM.fill(output.matrix, 0);
	    
		
	}
	
	
	Equation eq;
	ManagerTempVariables tempManager;
	AbstractProgrammer programmer;
	IEmitOperation coder;
	GenerateEquationCode codeGenerator;
	JavaTargetManagerFunctions mf;
	
	public EjmlExpressionCompiler( Scope scope, AbstractProgrammer programmer, ManagerTempVariables tempManager, boolean isTestTarget ) {
		this.programmer = programmer;
		Map<String, Object> variables = mapVariables(scope, Transpiler.instance().getSymbolTable());
		this.tempManager = tempManager;
		eq = new Equation();
		eq.setManagerTemp( tempManager );
		OperationCodeFactory factory = new OperationCodeFactory();
		mf = new JavaTargetManagerFunctions(factory, tempManager, programmer);
		coder = new EmitJavaOperation( mf );
		eq.setManagerFunctions(mf);
		mf.mapFunctions( scope, Transpiler.instance().getSymbolTable(), isTestTarget );
		
		for (String name : variables.keySet()) {
			try {
				eq.alias(variables.get(name), name);
			} catch (Exception x) {
				System.out.println(x.getMessage() + ": " + name);
			}
		}
	}
	
	public void setStaticImports(List<StaticImport> staticImports) {
		for (StaticImport si : staticImports) {
			JavaTargetManagerFunctions.GenericMethodFunction gmf = mf.new GenericMethodFunction(si.name, si.type);
			mf.add(gmf);
		}
	}
	
	static class EjmlImports {
		public String keyword;
		public String importText;
		
		public EjmlImports( String keyword, String importText ) {
			this.keyword = keyword;
			this.importText = importText;
		}
	}

	final EjmlImports[] ejmlImports = {
			new EjmlImports("LinearSolverDense", "org.ejml.interfaces.linsol.LinearSolverDense"),
			new EjmlImports("LinearSolverFactory_DDRM", "org.ejml.dense.row.factory.LinearSolverFactory_DDRM"),
			new EjmlImports("MatrixFeatures_DDRM", "org.ejml.dense.row.MatrixFeatures_DDRM"),
	};
	

	final String dummyPrefix = "asssignment$dummy = void(";
	final static Pattern reshapePattern = Pattern.compile("(\\w+)\\.reshape\\((.+),(.+)\\)");
	TreeSet<String> declaredTemps = new TreeSet<>();
	
	
	public void setTemporaries(TreeSet<String> declaredTemps) {
		this.declaredTemps = declaredTemps;
	}
	
	public boolean compile(String expression, List<String> imports, Scope currentScope ) {
		boolean isVoid = false;
		if (expression.indexOf('=') < 0) {
			isVoid = true;
			expression = dummyPrefix + expression + ")";
		}
		
		codeGenerator = new GenerateEquationCode(eq, coder, null, null, declaredTemps);
		if (! codeGenerator.generate(expression, false) ) {
			Transpiler.instance().logger().info(String.format("Compile: %s -X: %s", expression, codeGenerator.getLastError().getMessage()));
//			System.out.println(codeGenerator.getLastError().getMessage() + ": " + expression);
			//eq.getVariables().keySet().forEach(System.out::println);
			return false;
		}
		if (codeGenerator.getCode().isEmpty() || 
			(codeGenerator.getCode().size() == 1 && codeGenerator.getCode().get(0).trim().startsWith("//"))) {
			Transpiler.instance().logger().info(String.format("Compile: %s -Z", expression));
			return false;			
		}
		if (isVoid) {
			String line = codeGenerator.getCode().get(0);
			line = line.replace(dummyPrefix, "");
			if (line.startsWith("//"))
				line = line.substring(0, line.length()-1);
			codeGenerator.getCode().set(0, line);
		}
		Iterator<String> it = codeGenerator.getCode().iterator();
		while (it.hasNext()) {
			String line = it.next();
			for (EjmlImports match : ejmlImports) {
				if (line.contains(match.keyword)) {
					imports.add(match.importText);
				}
			}
			// remove reshapes of fixed size matrices
			Matcher matcher = reshapePattern.matcher(line);
			if (matcher.find()) {
				String target = matcher.group(1);
				Symbol array = Transpiler.instance().lookup(currentScope, target);
				if (array != null) {
					if (array.getDimensions() != null) {
						it.remove();
					}
				}
			}
		}
		Transpiler.instance().logger().info(String.format("Compile: %s ->: %s", expression, codeGenerator.getCode().toString()));
		return true;
	}
	
	public List<String> getHeader() {
		return Arrays.asList(codeGenerator.getHeader().toString().split("\n"));
	}
	
	public List<String> getCode() {
		return codeGenerator.getCode();
	}
	
	
	protected static void declareVariable( HashMap<String, Object> variables, String qualifiedName, Symbol symbol) {
		switch (symbol.getType()) {
		case "int":
			variables.put(qualifiedName, new Integer(0));
			break;
		case "float":
			variables.put(qualifiedName, new Double(0));
			break;
		case "array":
			variables.put(qualifiedName, new DMatrixRMaj(1,1));
			break;
		case "vector":
			variables.put(qualifiedName, new DMatrixRMaj(1));
			break;
		default:
			if (symbol.isClass() || symbol.isEnum() ) {
			} else if (symbol.isFunction()) {
			} else if (symbol.getType().contains("test")) {
			} else {
				//System.out.println("Unhandled type: " + symbol.toString() ); //throw new RuntimeException
			}
		}
		
	}
	
	public static Map<String, Object> mapVariables( Scope scope, SymbolTable symbolTable ) {
		HashMap<String, Object> variables = new HashMap<>();
		
		String prefix = "";
		while (scope.getLevelCount() > 0) {
			for (Symbol symbol : symbolTable.atScope(scope)) {
				if (symbol.isFunction())
					continue;
				String qualifiedName = prefix + symbol.getName();
				if (! variables.containsKey(qualifiedName)) {
					declareVariable( variables, qualifiedName, symbol );
				}
			}
			prefix = "this$";
			scope = scope.getParent();
		}
//		variables.keySet().forEach(System.out::println);
		return variables;
	}

}