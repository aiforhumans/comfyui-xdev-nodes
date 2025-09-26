# XDEV_MathBasic Node Documentation

## Overview
The **Math Basic Operations (XDev)** node provides essential mathematical operations with comprehensive error handling and precision control. This Phase 1 foundation node demonstrates XDev patterns for robust numerical computation with detailed validation.

## Features
- **7 Mathematical Operations**: add, subtract, multiply, divide, modulo, power, floor_divide
- **Type Flexibility**: Accepts both integers and floating-point numbers
- **Precision Control**: Configurable decimal places (0-15)
- **Error Prevention**: Division by zero and invalid operation detection
- **Dual Output**: Both float and integer results with calculation metadata

## Inputs

### Required
- **a** (FLOAT): First number for the mathematical operation
  - Range: -999,999 to 999,999
  - Step: 0.01
  - Default: 0.0
  - Accepts integers and decimals
  
- **b** (FLOAT): Second number for the mathematical operation  
  - Range: -999,999 to 999,999
  - Step: 0.01
  - Default: 1.0
  - Cannot be zero for division/modulo operations
  
- **operation** (DROPDOWN): Mathematical operation to perform
  - **add** (+): Addition
  - **subtract** (-): Subtraction
  - **multiply** (*): Multiplication  
  - **divide** (/): Division (true division)
  - **modulo** (%): Remainder after division
  - **power** (^): Exponentiation
  - **floor_divide** (//): Floor division (integer result)

### Optional
- **precision** (INT): Number of decimal places to round result
  - Range: 0-15
  - Default: 6
  - 0 for integer-like results
  
- **validate_input** (BOOLEAN): Enable comprehensive input validation
  - Default: True
  - Includes division by zero and invalid power checks

## Outputs
1. **result** (FLOAT): Mathematical result with specified precision
2. **result_int** (INT): Result converted to integer (truncated)
3. **calculation_info** (STRING): Detailed calculation information and metadata

## Usage Examples

### Basic Arithmetic
```
a: 15.5, b: 2.5, operation: "multiply"
Result: 38.75
Info: "15.5 * 2.5 = 38.75"
```

### Division with Precision
```
a: 22.0, b: 7.0, operation: "divide", precision: 3
Result: 3.143
Info: "22.0 / 7.0 = 3.143 (rounded to 3 decimals)"
```

### Power Operations
```
a: 2.0, b: 10.0, operation: "power"
Result: 1024.0
Info: "2.0 ^ 10.0 = 1024.0"
```

## Technical Details

### Performance Optimizations
- **Precomputed Operations**: All mathematical operations use precomputed operator mapping
- **Lazy Validation**: Optional validation can be disabled for high-performance scenarios
- **Efficient Precision**: Uses Python's built-in round() for optimal performance

### Error Handling
- **Division by Zero**: Comprehensive detection for divide, modulo, and floor_divide
- **Invalid Powers**: Prevents zero to negative power and negative to non-integer power
- **Overflow Protection**: Handles overflow errors with meaningful messages
- **Type Safety**: Validates input types with detailed error reporting

### Mathematical Operations Detail

| Operation | Symbol | Description | Error Conditions |
|-----------|---------|-------------|------------------|
| add | + | Standard addition | None |
| subtract | - | Standard subtraction | None |  
| multiply | * | Standard multiplication | Overflow possible |
| divide | / | True division (float result) | Division by zero |
| modulo | % | Remainder after division | Division by zero |
| power | ^ | Exponentiation | 0^(negative), negative^(non-integer) |
| floor_divide | // | Integer division (floor) | Division by zero |

### Precision Control
- **Range**: 0-15 decimal places
- **Rounding**: Uses Python's built-in round() function
- **Integer Output**: Always provides truncated integer version
- **Precision Metadata**: Indicates when rounding occurred

## Integration Patterns

### Universal Testing
```
InputDev(FLOAT) → MathBasic → OutputDev
```

### Multi-Step Calculations
```
InputDev(FLOAT) → MathBasic → MathBasic → OutputDev
```

### Type Conversion Workflows
```
InputDev(INT) → MathBasic → [Float/Int outputs] → OutputDev
```

## Best Practices

### Performance Optimization
- Disable validation for trusted, high-performance workflows
- Use appropriate precision (lower values for performance)
- Cache results for identical calculations in loops

### Error Prevention
- Always validate inputs when working with user data
- Check for division by zero in dynamic workflows
- Use range limits to prevent overflow conditions

### Workflow Design
- Use both float and integer outputs as needed
- Leverage calculation_info for debugging and documentation
- Chain operations for complex mathematical expressions

## Troubleshooting

### Common Errors
1. **Division by Zero**: Ensure second operand is non-zero for division operations
2. **Invalid Power**: Check base and exponent combinations for power operations
3. **Overflow**: Use smaller numbers or different operations for large calculations
4. **Precision Loss**: Increase precision setting for more accurate results

### Performance Issues
1. **Slow Validation**: Disable validation for trusted data sources
2. **Precision Overhead**: Use lower precision for faster calculations
3. **Memory Usage**: Consider result caching for repeated identical operations

### Type Compatibility
- All inputs accept both INT and FLOAT types
- Output provides both float and integer versions
- Use appropriate output type for downstream nodes

## Algorithm Implementation

### Operation Mapping
```python
_OPERATIONS = {
    "add": operator.add,
    "subtract": operator.sub,
    "multiply": operator.mul,
    "divide": operator.truediv,
    "modulo": operator.mod,
    "power": operator.pow,
    "floor_divide": operator.floordiv
}
```

### Validation Logic
1. **Type Validation**: Ensures numeric inputs
2. **Operation Validation**: Verifies operation exists
3. **Mathematical Validation**: Checks for invalid mathematical conditions
4. **Error Recovery**: Provides meaningful error messages and safe defaults

## Related Nodes
- **InputDev**: Generate test numbers for mathematical operations
- **OutputDev**: Analyze mathematical results and validate outputs
- **TextCase**: Convert mathematical results to different string formats
- **AppendSuffix**: Add units or labels to mathematical results