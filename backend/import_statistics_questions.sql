-- Statistics Questions Import Script
-- Comprehensive set of statistics learning questions
-- Run this after statistics_schema.sql

USE vocabulary_app;

-- First, ensure subjects and question types exist
INSERT IGNORE INTO subjects (name, code, description) VALUES 
    ('Statistics', 'STAT', 'Statistical concepts, methods, and analysis');

INSERT IGNORE INTO question_types (type_name, description) VALUES 
    ('multiple_choice', 'Multiple choice with one correct answer'),
    ('true_false', 'True or false question');

-- Get IDs for references
SET @stat_subject_id = (SELECT id FROM subjects WHERE code = 'STAT');
SET @mc_type_id = (SELECT id FROM question_types WHERE type_name = 'multiple_choice');
SET @tf_type_id = (SELECT id FROM question_types WHERE type_name = 'true_false');

-- ============================================
-- P-VALUES QUESTIONS
-- ============================================

INSERT INTO questions (subject_id, question_type_id, question_text, question_latex, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id, 
    'What does a p-value represent in hypothesis testing?',
    'P(\\text{data} | H_0 \\text{ is true})',
    'The p-value is the probability of observing data as extreme or more extreme than what was observed, assuming the null hypothesis is true.',
    'beginner');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct, explanation) VALUES
    (@last_q_id, 'The probability that the null hypothesis is true', FALSE, 'This is a common misconception. The p-value is NOT the probability that H0 is true.'),
    (@last_q_id, 'The probability of observing the data (or more extreme) if the null hypothesis is true', TRUE, 'Correct! This is the definition of a p-value.'),
    (@last_q_id, 'The probability that the alternative hypothesis is true', FALSE, 'The p-value relates to the null hypothesis, not the alternative.'),
    (@last_q_id, 'The probability of making a Type I error', FALSE, 'This is the significance level (alpha), not the p-value.');

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'If you obtain a p-value of 0.03 with a significance level of α = 0.05, what should you conclude?',
    'Since 0.03 < 0.05, we have sufficient evidence to reject the null hypothesis at the 5% significance level.',
    'intermediate');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'Fail to reject the null hypothesis', FALSE),
    (@last_q_id, 'Reject the null hypothesis', TRUE),
    (@last_q_id, 'Accept the alternative hypothesis with certainty', FALSE),
    (@last_q_id, 'The test is inconclusive', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @tf_type_id,
    'A smaller p-value provides stronger evidence against the null hypothesis.',
    'True. A smaller p-value indicates that the observed data would be less likely under the null hypothesis, providing stronger evidence against it.',
    'beginner');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'True', TRUE),
    (@last_q_id, 'False', FALSE);

-- ============================================
-- RESIDUALS QUESTIONS
-- ============================================

INSERT INTO questions (subject_id, question_type_id, question_text, question_latex, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What is a residual in regression analysis?',
    'e_i = y_i - \\hat{y}_i',
    'A residual is the difference between the observed value and the predicted value from the regression model.',
    'beginner');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct, explanation) VALUES
    (@last_q_id, 'The difference between observed and predicted values', TRUE, 'Correct! Residual = Observed - Predicted'),
    (@last_q_id, 'The slope of the regression line', FALSE, 'The slope is a parameter of the model, not a residual.'),
    (@last_q_id, 'The correlation coefficient', FALSE, 'The correlation coefficient measures linear association, not prediction error.'),
    (@last_q_id, 'The y-intercept of the regression line', FALSE, 'The intercept is a parameter, not a residual.');

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @tf_type_id,
    'In a good regression model, residuals should show a clear pattern when plotted against fitted values.',
    'False. Residuals should be randomly scattered with no clear pattern. A pattern indicates model inadequacy.',
    'intermediate');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'True', FALSE),
    (@last_q_id, 'False', TRUE);

INSERT INTO questions (subject_id, question_type_id, question_text, question_latex, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What assumption about residuals is required for valid inference in linear regression?',
    '\\epsilon_i \\sim N(0, \\sigma^2)',
    'For valid inference, we assume residuals are normally distributed with mean zero and constant variance (homoscedasticity).',
    'intermediate');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'Residuals are normally distributed with constant variance', TRUE),
    (@last_q_id, 'Residuals are uniformly distributed', FALSE),
    (@last_q_id, 'Residuals increase with fitted values', FALSE),
    (@last_q_id, 'Residuals are all positive', FALSE);

-- ============================================
-- LINEAR MODELS QUESTIONS
-- ============================================

INSERT INTO questions (subject_id, question_type_id, question_text, question_latex, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'In the simple linear regression model Y = β₀ + β₁X + ε, what does β₁ represent?',
    'Y = \\beta_0 + \\beta_1 X + \\epsilon',
    'β₁ is the slope coefficient, representing the expected change in Y for a one-unit increase in X.',
    'beginner');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'The y-intercept', FALSE),
    (@last_q_id, 'The slope - change in Y per unit change in X', TRUE),
    (@last_q_id, 'The error term', FALSE),
    (@last_q_id, 'The correlation coefficient', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, question_latex, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What does R² (coefficient of determination) measure in regression?',
    'R^2 = 1 - \\frac{SS_{res}}{SS_{tot}}',
    'R² measures the proportion of variance in the dependent variable explained by the independent variable(s). It ranges from 0 to 1.',
    'beginner');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'The strength of correlation only', FALSE),
    (@last_q_id, 'The proportion of variance explained by the model', TRUE),
    (@last_q_id, 'The standard error of regression', FALSE),
    (@last_q_id, 'The p-value of the model', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @tf_type_id,
    'A high R² value always indicates a good regression model.',
    'False. A high R² alone does not guarantee model quality. Check residual patterns, multicollinearity, and theoretical validity.',
    'intermediate');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'True', FALSE),
    (@last_q_id, 'False', TRUE);

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What is multicollinearity in multiple regression?',
    'Multicollinearity occurs when predictor variables are highly correlated with each other, making it difficult to isolate individual effects.',
    'intermediate');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'High correlation among predictor variables', TRUE),
    (@last_q_id, 'Non-linear relationship between X and Y', FALSE),
    (@last_q_id, 'Heteroscedasticity of residuals', FALSE),
    (@last_q_id, 'Outliers in the data', FALSE);

-- ============================================
-- ANOVA QUESTIONS
-- ============================================

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What does ANOVA (Analysis of Variance) test?',
    'ANOVA tests whether there are statistically significant differences among the means of three or more independent groups.',
    'beginner');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'Differences between two means only', FALSE),
    (@last_q_id, 'Differences among three or more group means', TRUE),
    (@last_q_id, 'Correlation between two variables', FALSE),
    (@last_q_id, 'Variance within a single group', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, question_latex, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'In ANOVA, what is the F-statistic?',
    'F = \\frac{MS_{between}}{MS_{within}} = \\frac{\\text{Between-group variance}}{\\text{Within-group variance}}',
    'The F-statistic is the ratio of between-group variance to within-group variance. Large F values suggest group means differ significantly.',
    'intermediate');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'The ratio of between-group to within-group variance', TRUE),
    (@last_q_id, 'The sum of squared residuals', FALSE),
    (@last_q_id, 'The correlation coefficient', FALSE),
    (@last_q_id, 'The difference between largest and smallest means', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @tf_type_id,
    'ANOVA assumes that the populations being compared have equal variances (homogeneity of variance).',
    'True. This is one of the key assumptions of ANOVA, also known as homoscedasticity assumption.',
    'beginner');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'True', TRUE),
    (@last_q_id, 'False', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What is the purpose of post-hoc tests after ANOVA?',
    'Post-hoc tests (e.g., Tukey HSD, Bonferroni) identify which specific groups differ from each other after a significant ANOVA result.',
    'intermediate');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'To determine which specific groups differ', TRUE),
    (@last_q_id, 'To calculate the F-statistic', FALSE),
    (@last_q_id, 'To test the normality assumption', FALSE),
    (@last_q_id, 'To increase statistical power', FALSE);

-- ============================================
-- ANCOVA QUESTIONS
-- ============================================

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What is ANCOVA (Analysis of Covariance)?',
    'ANCOVA combines ANOVA and regression by testing group differences while controlling for continuous covariates.',
    'intermediate');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'ANOVA that controls for continuous covariates', TRUE),
    (@last_q_id, 'ANOVA for non-normal data', FALSE),
    (@last_q_id, 'ANOVA with only two groups', FALSE),
    (@last_q_id, 'ANOVA without assumptions', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What is a covariate in ANCOVA?',
    'A covariate is a continuous variable that is correlated with the dependent variable and included to reduce error variance.',
    'intermediate');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'A continuous variable controlled for in the analysis', TRUE),
    (@last_q_id, 'A categorical independent variable', FALSE),
    (@last_q_id, 'The dependent variable', FALSE),
    (@last_q_id, 'An interaction term', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @tf_type_id,
    'In ANCOVA, we assume that the relationship between the covariate and dependent variable is the same across all groups (homogeneity of regression slopes).',
    'True. This is a critical assumption of ANCOVA. If violated, consider including interaction terms.',
    'advanced');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'True', TRUE),
    (@last_q_id, 'False', FALSE);

-- ============================================
-- ADDITIONAL CORE CONCEPTS
-- ============================================

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What is the Central Limit Theorem?',
    'The CLT states that the sampling distribution of the mean approaches a normal distribution as sample size increases, regardless of population distribution.',
    'beginner');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'Sample means follow a normal distribution for large samples', TRUE),
    (@last_q_id, 'All populations are normally distributed', FALSE),
    (@last_q_id, 'Large samples always have small variance', FALSE),
    (@last_q_id, 'The mean equals the median in all distributions', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What is the difference between Type I and Type II errors?',
    'Type I error: Rejecting a true null hypothesis (false positive). Type II error: Failing to reject a false null hypothesis (false negative).',
    'beginner');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'Type I: False positive, Type II: False negative', TRUE),
    (@last_q_id, 'Type I: False negative, Type II: False positive', FALSE),
    (@last_q_id, 'Both are the same error', FALSE),
    (@last_q_id, 'Type I occurs with small samples only', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, question_latex, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What does a confidence interval represent?',
    'CI = \\bar{x} \\pm z \\cdot \\frac{\\sigma}{\\sqrt{n}}',
    'A confidence interval provides a range of plausible values for a population parameter. A 95% CI means we are 95% confident the true parameter lies within the interval.',
    'beginner');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'A range of plausible values for a population parameter', TRUE),
    (@last_q_id, 'The probability the parameter equals a specific value', FALSE),
    (@last_q_id, 'The standard error of the estimate', FALSE),
    (@last_q_id, 'The p-value of the test', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @tf_type_id,
    'Correlation implies causation.',
    'False. This is one of the most important principles in statistics. Correlation does NOT imply causation. Other factors, confounding, or reverse causation may be at play.',
    'beginner');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'True', FALSE),
    (@last_q_id, 'False', TRUE);

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What is statistical power?',
    'Power is the probability of correctly rejecting a false null hypothesis (1 - β). Higher power means better ability to detect true effects.',
    'intermediate');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'The probability of correctly rejecting a false null hypothesis', TRUE),
    (@last_q_id, 'The probability of making a Type I error', FALSE),
    (@last_q_id, 'The sample size needed', FALSE),
    (@last_q_id, 'The significance level', FALSE);

INSERT INTO questions (subject_id, question_type_id, question_text, explanation, difficulty_level) 
VALUES (@stat_subject_id, @mc_type_id,
    'What is heteroscedasticity?',
    'Heteroscedasticity occurs when the variance of residuals is not constant across levels of the independent variable. This violates a key regression assumption.',
    'intermediate');
SET @last_q_id = LAST_INSERT_ID();
INSERT INTO answer_options (question_id, option_text, is_correct) VALUES
    (@last_q_id, 'Non-constant variance of residuals', TRUE),
    (@last_q_id, 'Non-linear relationships', FALSE),
    (@last_q_id, 'Missing data', FALSE),
    (@last_q_id, 'Outliers in predictors', FALSE);

SELECT 'Statistics questions imported successfully!' as Status, 
       COUNT(*) as QuestionCount 
FROM questions 
WHERE subject_id = @stat_subject_id;
