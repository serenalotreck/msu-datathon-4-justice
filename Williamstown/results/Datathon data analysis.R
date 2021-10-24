#Datathon regression analysis
stuff<-Police_by_race
stuff$Name<-as.factor(stuff$Name)
stuff$Status<-as.factor(stuff$Status)

stuff<-aggregate(cbind(U, W, A, B) ~ Name, data = stuff, FUN = sum, na.rm = TRUE)
print(stuff)

library(car)
fit <- lm(W ~ U + A + B, data=stuff)
summary(fit) #Number of traffic stops on "white" people is correlated with "unknown" and "Asian" categories.
  #It is barely non-significant for "black/AA."
outlierTest(fit) #Scott Skorupski is an outlier in this data set.
qqPlot(fit)

#stuff<-stuff[!(stuff$Name=="Kevin_Garner"),] #Outlier removal

x <- stuff$W
y <- stuff$B
z <- stuff$U
a <- stuff$A
# Plot with main and axis titles
# Add regression line
plot(x, y, main = "Number of Traffic Stops by Race",
     xlab = "Number of traffic stops (White)", ylab = "Number of traffic stops (Black/AA)",
     pch = 19, frame = FALSE)
abline(lm(y ~ x, data = stuff), col = "blue")
scatterplot(y ~ x, data = stuff, main = "Scatterplot of Traffic Stops on White versus Black/AA People",
            ylab = "Black/AA", xlab = "White")
